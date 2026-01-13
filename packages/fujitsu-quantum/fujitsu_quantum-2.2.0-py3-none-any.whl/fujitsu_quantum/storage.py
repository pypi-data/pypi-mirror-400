# (C) 2024 Fujitsu Limited
from __future__ import annotations

import io
import json
import os.path
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from http import HTTPStatus
from io import BytesIO
from os import PathLike
from pathlib import Path
from typing import Any, Union, Optional
from zipfile import ZipFile

from fujitsu_quantum import logging
from fujitsu_quantum.config import Config
from fujitsu_quantum.requests import FQCRequest, Request, RequestError
from fujitsu_quantum.types import single_to_multiple_values, to_api_operator, to_sdk_operator
from fujitsu_quantum.utils import numpy_array_to_python_list, json_dumps


@dataclass
class ObjectReference:
    """A reference to an object uploaded to Quantum Cloud."""
    key: str


class StorageObjectDownloadError(Exception):
    """
    Attributes:
        url: storage object URL
        message: error message.
    """

    def __init__(self, url: str, message: str):
        super().__init__(url, message)
        self.url = url
        self.message = message

    def __str__(self):
        return f'{self.message}. URL: {self.url}'


class StorageService:

    ENDPOINT: str = Config.api_base + '/tasks'

    _OBJECT_EXT: str = ".zip"
    _KEY_PATTERN_FOR_USERS = re.compile('([a-zA-Z0-9][a-zA-Z0-9_.-]*/)*[a-zA-Z0-9_][a-zA-Z0-9_.-]*$')
    """The key pattern that users can specify. Note that keys for auto-uploaded data start with '_/' and do not satisfy this pattern."""

    _ALLOWED_PARAMS = ['program', 'operator', 'parameter_values', 'n_shots', 'qubit_allocation']
    """The parameters that can be uploaded to the storage."""

    CODE_FILE_PATH_PATTERN = re.compile(r'^code/\d+.(qasm|qpy)$')

    @staticmethod
    def upload(items: dict[str, dict[str, Any]], overwrite: bool = False) -> dict[str, ObjectReference]:
        """Uploads parameter values to the object storage.

        Args:
            items (dict[str, dict[str, Any]]): a dict of key and parameter-values pairs. The parameter-values is a dict
                                               of parameter name and value pairs.
            overwrite (bool): whether to overwrite existing objects having the same keys in the storage.

        Returns:
            dict[str, ObjectReference]: a dict of key and ObjectReference pairs.
        """
        return StorageService._upload(items, overwrite, validation_for_users=True, normalization=True)

    @staticmethod
    def _upload(items: dict[str, dict[str, Any]], overwrite: bool = False,
                validation_for_users: bool = False, normalization: bool = False) -> dict[str, ObjectReference]:
        """Uploads parameter values to the object storage.

        Args:
            items (dict[str, dict[str, Any]]): a dict of key and parameter-values pairs. The parameter-values is a dict
                                               of parameter name and value pairs.
            overwrite (bool): whether to overwrite existing objects having the same keys in the storage.

        Returns:
            dict[str, ObjectReference]: a dict of key and ObjectReference pairs.
        """
        if validation_for_users:
            invalid_keys = list(filter(lambda k: not StorageService._KEY_PATTERN_FOR_USERS.match(k), items.keys()))
            if invalid_keys:
                raise ValueError(f'Invalid keys: {invalid_keys}.'
                                 f' Keys must start with an alphanumeric character and can contain characters in [a-zA-Z0-9._-/].')

            all_invalid_params = []
            for param_value_dicts in items.values():
                all_invalid_params.extend(list(filter(lambda k: k not in StorageService._ALLOWED_PARAMS, param_value_dicts.keys())))
            if all_invalid_params:
                raise ValueError(f'The parameters that can be uploaded are {StorageService._ALLOWED_PARAMS},'
                                 f' but {all_invalid_params} have been specified.')

        register_files_request_body = {
            "mode": "register_task_files",
            "overwrite": overwrite,
            "files": [key + StorageService._OBJECT_EXT for key in items.keys()]
        }

        upload_params = FQCRequest.post(status_code=HTTPStatus.OK, url=StorageService.ENDPOINT,
                                        data=json_dumps(register_files_request_body)).json()

        # TODO parallel uploads for better performance
        result = {}
        for key, upload_param in zip(items, upload_params):
            with io.BytesIO() as zip_buffer:
                zip_buffer.name = key + StorageService._OBJECT_EXT
                with ZipFile(file=zip_buffer, mode="w") as zip_arch:
                    if normalization:
                        # Normalize the given parameter values to satisfy the followings.
                        # Note that the normalizations 2--4 are also performed in Task._prepare_primitive_task_request(...).
                        # TODO consider performing extract-method refactoring on the normalization logics.
                        # 1. The parameter name 'program' is renamed to 'code'
                        # 2. numpy types are converted into corresponding python types
                        # 3. single values are not used (e.g., type(code) is always list)
                        # 4. "operator" values are in the Web API format.
                        if 'program' in items[key]:
                            items[key]['code'] = items[key].pop('program')
                        if 'n_shots' in items[key]:
                            items[key]['n_shots'] = numpy_array_to_python_list(items[key]['n_shots'])
                        if 'parameter_values' in items[key]:
                            items[key]['parameter_values'] = numpy_array_to_python_list(items[key]['parameter_values'])

                        param_values, single_value_params = single_to_multiple_values(items[key])
                        if 'operator' in param_values:
                            param_values['operator'] = to_api_operator(param_values['operator'])
                    else:
                        param_values = items[key]
                        single_value_params = []

                    for param, value in param_values.items():
                        if param == 'code':
                            # code can be either str (OpenQASM code) or bytes (QPY data)
                            for i, one_data in enumerate(value):
                                if isinstance(one_data, bytes):
                                    zip_arch.writestr(zinfo_or_arcname=f'{param}/{i:04d}.qpy', data=one_data)
                                else:
                                    zip_arch.writestr(zinfo_or_arcname=f'{param}/{i:04d}.qasm', data=one_data)
                        else:
                            zip_arch.writestr(zinfo_or_arcname=f'{param}.json', data=json_dumps(value))

                    zip_arch.writestr(zinfo_or_arcname='metadata.json',
                                      data=json_dumps({'sdkSingleValueParams': single_value_params}))

                zip_buffer.seek(0)
                Request.post(exp_status_code=HTTPStatus.NO_CONTENT,
                             url=upload_param['url'],
                             data=upload_param['fields'],
                             files={'file': (os.path.basename(zip_buffer.name), zip_buffer, 'application/zip')})

            result[key] = ObjectReference(key)

        return result

    @staticmethod
    def _download(url_or_path: str, use_local_storage: bool) -> dict[str, Any]:

        with io.BytesIO() as zip_buffer:
            if use_local_storage:
                with open(url_or_path, 'rb') as f:
                    zip_buffer.write(f.read())
            else:
                resp = Request.get(url=url_or_path)
                zip_buffer.write(resp.content)

            zip_buffer.flush()
            zip_buffer.seek(0)
            try:
                result = StorageService._extract_zip_object(zip_buffer)
            except Exception as e:
                log_file_path = StorageService._write_error_log(f'The storage object is corrupted. Path: {url_or_path}.\n'
                                                                f'Error details: {type(e)}. {e}')
                raise StorageObjectDownloadError(url_or_path, f'The storage object is corrupted.'
                                                                f' Error details have been saved to {log_file_path}')

        return result

    @staticmethod
    def _extract_zip_object(zip_buffer: BytesIO):
        result = {}
        with ZipFile(zip_buffer, 'r') as zip_arch:
            json_file_path_list = zip_arch.namelist()

            # The 'code' value is stored in different ways depending on the SDK version that uploaded the object.
            # v2.2.0 or higher
            # - code/\d+.(qasm|qpy)
            # v2.1.0 or lower
            # - code.json
            code_file_paths = list(filter(lambda p: StorageService.CODE_FILE_PATH_PATTERN.match(p), json_file_path_list))
            if code_file_paths:
                code_values = []
                for code_file_path in sorted(code_file_paths):
                    with zip_arch.open(code_file_path) as code_file:
                        if code_file_path.endswith('.qpy'):
                            code_values.append(code_file.read())
                        else:
                            code_values.append(code_file.read().decode('utf-8'))
                result['code'] = code_values
                # Remove code file paths from json_file_path_list to avoid double processing
                json_file_path_list = [p for p in json_file_path_list if p not in code_file_paths]
            else:
                # code.json may exist, and will be processed below
                pass

            # process files other than code/*** files
            json_file_path_list = [p for p in json_file_path_list if not StorageService.CODE_FILE_PATH_PATTERN.match(p)]
            for json_file_path in json_file_path_list:
                param_name = Path(json_file_path).stem
                with zip_arch.open(json_file_path) as json_file:
                    value = json.loads(json_file.read())
                    if param_name == 'operator':
                        value = to_sdk_operator(value)
                    result[param_name] = value

        metadata: dict | None = result.pop('metadata', None)
        if metadata is not None:
            for param_name in metadata['sdkSingleValueParams']:
                result[param_name] = result[param_name][0]

        return result

    @staticmethod
    def _write_error_log(err_msg: str):
        err_msg_header = f'StorageFileError occurred at {str(datetime.now(timezone.utc))} UTC.\n----------------------------\n'
        return logging.write_error_log(f'{err_msg_header}{err_msg}')

    @staticmethod
    def _upload_hybrid_program(key: str, zip_buffer: BytesIO, overwrite: bool = False):
        register_files_request_body = {
            "mode": "register_task_files",
            "overwrite": overwrite,
            "files": [key + StorageService._OBJECT_EXT]
        }

        upload_param = FQCRequest.post(status_code=HTTPStatus.OK, url=StorageService.ENDPOINT,
                                       data=json_dumps(register_files_request_body)).json()[0]

        zip_file_name = os.path.basename(key) + StorageService._OBJECT_EXT
        Request.post(exp_status_code=HTTPStatus.NO_CONTENT,
                     url=upload_param['url'],
                     data=upload_param['fields'],
                     files={'file': (zip_file_name, zip_buffer, 'application/zip')})

    @staticmethod
    def _download_hybrid_program_result(object_url: str, save_dir: Union[str, PathLike],
                                        get_fresh_object_url: Callable[[], str]):
        try:
            # TODO suppress the error log file output when the url is expired (403 error)
            resp = Request.get(url=object_url)
        except RequestError:
            # Since the pre-signed URL can be expired, obtain a new pre-signed URL to download the result data
            resp = Request.get(url=get_fresh_object_url())

        Path(save_dir).mkdir(parents=True, exist_ok=True)
        with ZipFile(BytesIO(resp.content)) as zip_arch:
            zip_arch.extractall(path=save_dir)


def resolve_raw_ref(param_name: str, value: Optional[dict[str, Any]], cache: dict[str, dict[str, Any]])\
        -> Optional[Union[ObjectReference, Any]]:

    if value is None:
        return None

    if 'raw' in value:
        return value['raw']

    if 'ref' in value:
        object_path = value['ref']
        if not object_path.startswith('https://'):
            return ObjectReference(object_path[:-len(StorageService._OBJECT_EXT)])
    else:
        object_path = f'{Config.local_storage_dir}/{value["local-ref"]}'

    # TODO support lazy download; i.e., download objects when Task.<property> is called for the first time
    if object_path in cache:
        return cache[object_path][param_name]
    else:
        param_values = StorageService._download(object_path, use_local_storage=('local-ref' in value))
        cache[object_path] = param_values
        return param_values[param_name]
