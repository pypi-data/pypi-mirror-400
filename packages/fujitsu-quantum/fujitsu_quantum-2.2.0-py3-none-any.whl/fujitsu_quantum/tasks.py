# (C) 2024 Fujitsu Limited

from __future__ import annotations

import os
import re
import time
import typing
from datetime import datetime, timezone
from enum import Enum
from io import BytesIO
from os import PathLike
from pathlib import Path
from pprint import pformat
from typing import Any, Optional, Union
from uuid import UUID, uuid4
from zipfile import ZipFile

from cryptography.fernet import Fernet

from fujitsu_quantum.api.api import create_task, get_task, cancel_task, delete_task, get_tasks
from fujitsu_quantum.auth import FQCAuth
from fujitsu_quantum.config import Config
from fujitsu_quantum.results import Result
from fujitsu_quantum.storage import ObjectReference, StorageService, resolve_raw_ref
from fujitsu_quantum.types import APIOperator, Integer, Operator, ParameterValues, QuantumCircuit, QubitAllocation, \
    to_sdk_operator, to_api_operator, single_to_multiple_values, to_single_value
from fujitsu_quantum.utils import snake_to_camel_keys, camel_to_snake_keys, remove_none_values, \
    numpy_array_to_python_list, find_duplicates, json_dumps

if typing.TYPE_CHECKING:
    from fujitsu_quantum.devices import Device


_MAX_QPY_VERSION = 15
_MIN_QPY_VERSION = 13


def _is_operator_small_sized(api_operator: list[APIOperator]) -> bool:
    # The complexity of len(list) is O(1), which is much faster than calling json.dumps(list).
    # So, we roughly check the data size using len(list) before checking the actual size using json.dumps(list)
    cumulative_nr_of_terms = 0

    for single_api_op in api_operator:
        cumulative_nr_of_terms += len(single_api_op)
        if cumulative_nr_of_terms > Task.MAX_RAW_PARAM_SIZE:
            return False

    # Proceed with detail calculation with json.dumps(list)
    # initial 2 bytes for operators list brackets [OP1,  OP2, ...]
    cumulative_size: int = 2

    for single_api_op in api_operator:
        # initial 2 bytes for single operator terms list brackets [TERM1, TERM2, ...]
        cumulative_size += 2

        # add each operator term size
        for op_term in single_api_op:
            cumulative_size += len(json_dumps(op_term))
            if cumulative_size > Task.MAX_RAW_PARAM_SIZE:
                break

    return cumulative_size <= Task.MAX_RAW_PARAM_SIZE


def _should_submit_as_raw(param: str, value: list[Any]) -> bool:
    if param == 'operator':
        return _is_operator_small_sized(value)
    elif param == 'code':
        # if one of the values is bytes (i.e., QPY data), it should be submitted as ref;
        # otherwise, raw or ref is decided based on the data size like other parameters.
        if any(isinstance(one_val, bytes) for one_val in value):
            return False

    tmp_str = str(value)
    # for efficiency, we check the data size using len(str) before using str.encode()
    return len(tmp_str) <= Task.MAX_RAW_PARAM_SIZE and len(tmp_str.encode('utf-8')) <= Task.MAX_RAW_PARAM_SIZE


def _serialize_code(program: str | list[str] | QuantumCircuit | list[QuantumCircuit] | ObjectReference) -> str | list[str] | bytes | list[bytes] | ObjectReference:
    """Serialize the given program for task submission.
    For Qiskit QuantumCircuit objects, serialize them into OpenQASM strings or QPY bytes, mainly depending on their sizes.
    For ObjectReference objects, return them as-is."""

    if isinstance(program, ObjectReference):
        return program

    is_single_value = False
    if not isinstance(program, list):
        is_single_value = True
        program = [program]

    serialized_data_list: list[str | bytes] = []
    for one_prg in program:
        if isinstance(one_prg, str):
            serialized_data_list.append(one_prg)
        else:
            module_name = one_prg.__class__.__module__
            if module_name.startswith('qiskit.'):
                one_prg_circuit: QuantumCircuit = one_prg  # type: ignore[assignment]

                # Serialize in QPY format if its size is large (i.e., > Task.MAX_RAW_PARAM_SIZE); otherwise, serialize in OpenQASM format.
                # Roughly estimate the size of serialized data by checking the number of gate instructions.
                # One gate instruction in OpenQASM format roughly takes 10 bytes (e.g., "cx $0, $1;").
                #
                # Use the largest QPY version such that it is supported by the installed Qiskit version and is between _MIN_QPY_VERSION and _MAX_QPY_VERSION.
                # If such a QPY version does not exist, fall back to OpenQASM serialization.
                from qiskit import qpy

                # Determine the QPY version to use
                if hasattr(qpy.common, 'QPY_COMPATIBILITY_VERSION'):  # old versions of Qiskit may not have this attribute
                    qpy_compatibility_version = qpy.common.QPY_COMPATIBILITY_VERSION
                else:
                    qpy_compatibility_version = -1

                if _MIN_QPY_VERSION <= qpy.common.QPY_VERSION <= _MAX_QPY_VERSION:
                    qpy_version = qpy.common.QPY_VERSION
                elif _MIN_QPY_VERSION <= qpy_compatibility_version <= _MAX_QPY_VERSION:  # qpy.common.QPY_VERSION is always greater than compatibility version
                    qpy_version = _MAX_QPY_VERSION
                else:
                    # fall back to OpenQASM serialization
                    qpy_version = None

                # Serialize
                serialized_one_data: str | bytes
                if (qpy_version is not None) and (len(one_prg_circuit.data) > Task.MAX_RAW_PARAM_SIZE / 10):
                    from io import BytesIO
                    with BytesIO() as qpy_buffer:
                        qpy.dump(one_prg, qpy_buffer, version=qpy_version)
                        qpy_buffer.flush()
                        serialized_one_data = qpy_buffer.getvalue()
                else:
                    from fujitsu_quantum.plugins.qiskit.qasm import to_qasm as qiskit_circuit_to_qasm
                    serialized_one_data = qiskit_circuit_to_qasm(one_prg_circuit)

                serialized_data_list.append(serialized_one_data)
            else:
                raise ValueError(f'The "program" argument must be OpenQASM code, Qiskit QuantumCircuit, ObjectReference, or list of them.')

    if is_single_value:
        return serialized_data_list[0]
    else:
        return serialized_data_list


class Task:

    DEFAULT_SHOTS: int = 1024
    MAX_RAW_PARAM_SIZE = 2 * 1024  # 2kB

    class Status(str, Enum):
        QUEUED = 'QUEUED'
        RUNNING = 'RUNNING'
        COMPLETED = 'COMPLETED'
        FAILED = 'FAILED'
        CANCELLING = 'CANCELLING'
        CANCELLED = 'CANCELLED'

    class Type(str, Enum):
        # To avoid circular imports, other *.py files use the following string literals. When changing the below
        # literal values, it needs to change other files as well.
        SAMPLING = 'sampling'
        ESTIMATION = 'estimation'
        HYBRID = 'hybrid'

    class EstimationMethod(str, Enum):
        SAMPLING = 'sampling'
        STATE_VECTOR = 'state_vector'

    class ROErrorMitigation(str, Enum):
        NONE = 'none'
        PSEUDO_INVERSE = 'pseudo_inverse'

    @classmethod
    def submit(cls,
               device: Device,
               task_type: Type,
               program: Union[str, list[str], QuantumCircuit, list[QuantumCircuit], ObjectReference],
               n_shots: Optional[Union[Integer, list[Integer], 'numpy.typing.NDArray', ObjectReference]] = None,
               operator: Optional[Union[Operator, list[Operator], ObjectReference]] = None,
               method: Optional[Union[Task.EstimationMethod, str]] = None,
               parameter_values: Optional[Union[ParameterValues, list[ParameterValues], 'numpy.typing.NDArray', ObjectReference]] = None,
               name: Optional[str] = None,
               note: Optional[str] = None,
               **configs) -> Task:

        if task_type == Task.Type.HYBRID:
            configs_copy = configs.copy()
            task_config_path = configs_copy.pop('task_config_path')
            request_body, auto_uploaded_param_values\
                = Task._prepare_hybrid_task_request(device=device,
                                                    program_paths=program,
                                                    task_config_path=task_config_path,
                                                    name=name,
                                                    note=note,
                                                    **configs_copy)
        else:
            request_body, auto_uploaded_param_values\
                = Task._prepare_primitive_task_request(device=device,
                                                       task_type=task_type,
                                                       code=program,
                                                       n_shots=n_shots,
                                                       method=method,
                                                       operator=operator,
                                                       parameter_values=parameter_values,
                                                       name=name,
                                                       note=note,
                                                       **configs)

        resp = create_task(request_body)

        # Replace ref with raw for auto-uploaded params so that each Task.<param> returns a raw value
        # rather than an ObjectReference object.
        # Also, inject virtual parameters (e.g., code_path) to request_body so that users can access them
        # via Task.<virtual-param>s.
        ref_params_under_configs = ['qubitAllocation']
        for param, value in auto_uploaded_param_values.items():
            if param in ref_params_under_configs:
                request_body['configs'][param] = {'raw': value}
            else:
                request_body[param] = {'raw': value}

        return Task({**request_body, **resp})

    @staticmethod
    def _is_qpu(device: Device) -> bool:
        ## Note: it should compare against Device.Type.QPU instead of 'QPU', but it causes a circular import.
        return device.device_type.upper() == 'QPU'

    @staticmethod
    def _prepare_hybrid_task_request(device: Device,
                                     program_paths: list[Union[str, PathLike]],
                                     task_config_path: Union[str, PathLike],
                                     name: Optional[str],
                                     note: Optional[str],
                                     **configs) -> tuple[dict[str, Any], dict[str, Any]]:

        with BytesIO() as zip_buffer:
            with ZipFile(zip_buffer, 'w') as zip_file:
                data_dir_in_zip = 'data'
                zip_file.writestr(data_dir_in_zip + '/', '')  # add the directory entries

                # add user programs to the directory "data/program" in the zip file
                program_dir_in_zip = 'data/program'
                zip_file.writestr(program_dir_in_zip + '/', '')

                norm_program_paths = list(map(lambda p: str(Path(p).resolve(strict=True)), program_paths))
                norm_program_names = list(map(lambda p: os.path.basename(p), norm_program_paths))
                duplicated_names = find_duplicates(norm_program_names)
                if duplicated_names:
                    raise ValueError(f'File and directory names in program_paths must be unique,'
                                     f' but the following names are duplicated: {duplicated_names}')

                for prg_path, prg_name in zip(norm_program_paths, norm_program_names):
                    prg_path_in_zip = os.path.join(program_dir_in_zip, prg_name)
                    zip_file.write(prg_path, prg_path_in_zip)
                    if os.path.isdir(prg_path):
                        for dir_path, dir_names, file_names in os.walk(prg_path, followlinks=True):
                            arcname_prefix_path = os.path.join(prg_path_in_zip, os.path.relpath(dir_path, prg_path))
                            for directory in sorted(dir_names):
                                zip_file.write(filename=os.path.join(dir_path, directory),
                                               arcname=os.path.normpath(os.path.join(arcname_prefix_path, directory)))
                            for file in sorted(file_names):
                                zip_file.write(filename=os.path.join(dir_path, file),
                                               arcname=os.path.normpath(os.path.join(arcname_prefix_path, file)))

                # add the task config file to the zip file
                task_config = str(Path(task_config_path).resolve(strict=True))
                zip_file.write(task_config, 'data/task-config.json')
                # TODO support requirements.txt

                # add the SDK home dir to the zip file
                config_dir_in_zip = '.fujitsu-quantum'
                zip_file.write(Config.config_dir, config_dir_in_zip)

                # add the SDK config file to the zip file
                config_file_path = os.path.join(Config.config_dir, Config.config_file_name)
                if os.path.exists(config_file_path):
                    zip_file.write(f'{Config.config_dir}/{Config.config_file_name}',
                                   f'{config_dir_in_zip}/{Config.config_file_name}')

                # encrypt the credentials file and add the encrypted data to the zip file
                with open(str(FQCAuth.CREDENTIALS_FILE_PATH), 'rb') as cred_file:
                    cred_bytes = cred_file.read()

                encryption_key = Fernet.generate_key()
                fernet = Fernet(encryption_key)
                encrypted_cred_bytes = fernet.encrypt(cred_bytes)
                zip_file.writestr(f'{config_dir_in_zip}/{FQCAuth.CREDENTIALS_FILE_NAME}.enc', encrypted_cred_bytes)

            zip_buffer.seek(0)

            auto_ref_key = Task._generate_auto_ref_key('hybrid_program')
            StorageService._upload_hybrid_program(auto_ref_key, zip_buffer)

        request_body = {
            'device': device.device_id,
            'type': 'hybrid',
            'code': {'ref': auto_ref_key + StorageService._OBJECT_EXT},
            'name': name,
            'note': note,
            'configs': snake_to_camel_keys(configs),
            'internal': {
                'encryptionKey': encryption_key.decode(encoding='utf-8', errors='strict'),
            },
        }

        request_body = remove_none_values(request_body)

        return request_body, {'code': None, 'codePaths': program_paths, 'configPath': task_config_path}

    @staticmethod
    def _prepare_primitive_task_request(device: Device,
                                        task_type: Type,
                                        code: Union[str, list[str], QuantumCircuit, list[QuantumCircuit], ObjectReference],
                                        n_shots: Optional[Union[Integer, list[Integer], ObjectReference]],
                                        method: Optional[Task.EstimationMethod],
                                        operator: Optional[Union[Operator, list[Operator], ObjectReference]],
                                        parameter_values: Optional[Union[ParameterValues, list[ParameterValues], ObjectReference]],
                                        name: Optional[str],
                                        note: Optional[str],
                                        **configs) -> tuple[dict[str, Any], dict[str, Any]]:

        # Note that some of the normalization logics below are also performed in StorageService._upload(...)

        # Remove user-unspecified values (i.e., None values) from the configs
        configs = remove_none_values(configs)

        # Add the parent (enclosing) hybrid-task ID
        if Config.in_hybrid_env:
            configs['hybridTaskId'] = Config.hybrid_task_id

        # Serialize the program code for task submission
        serialized_code = _serialize_code(code)

        ###
        ### Convert numpy dtypes to Python native types.
        ### The target parameters of the conversion are n_shots, operator, and parameter_values.
        ### The other parameters (e.g., seed_transpilation) are not allowed to be specified with numpy data types.
        ### Specifying numpy data types for the other parameters can cause errors when, e.g., JSON serialization
        ### in the SDK and server-side validation.
        ###
        if (n_shots is not None) and (not isinstance(n_shots, ObjectReference)):
            n_shots = numpy_array_to_python_list(n_shots)
        if (parameter_values is not None) and (not isinstance(parameter_values, ObjectReference)):
            parameter_values = numpy_array_to_python_list(parameter_values)

        ###
        ### Wrap a single value with a list if the parameter can be specified as a list.
        ### Prerequisite: numpy data types must be converted into Python native data types.
        ###
        single_value_allowed_param_values = {'code': serialized_code,
                                             'n_shots': n_shots,
                                             'operator': operator,
                                             'parameter_values': parameter_values,
                                             'qubit_allocation': configs.get('qubit_allocation', None)}

        converted_param_values, single_value_params = single_to_multiple_values(single_value_allowed_param_values)
        serialized_code = converted_param_values['code']
        n_shots = converted_param_values['n_shots']
        operator = converted_param_values['operator']
        parameter_values = converted_param_values['parameter_values']
        qubit_allocation = converted_param_values['qubit_allocation']
        if single_value_params:
            configs['sdk_single_value_params'] = single_value_params

        ###
        ### Set default values
        ###
        if Task._is_qpu(device):
            if 'ro_error_mitigation' not in configs:
                configs['ro_error_mitigation'] = Task.ROErrorMitigation.NONE
            if 'estimation_dop' not in configs:
                configs['estimation_dop'] = 1
        else:
            if 'n_per_node' not in configs:
                configs['n_per_node'] = 1

        if (n_shots is None
                and (task_type == Task.Type.SAMPLING or (task_type == Task.Type.ESTIMATION and method == Task.EstimationMethod.SAMPLING))):
            n_shots = [Task.DEFAULT_SHOTS]

        ###
        ### Validating parameter values
        ### Prerequisite: single values must be converted into multiple values via single_to_multiple_values(...).
        ###
        Task._validate_parameter_values(device=device, task_type=task_type, method=method, operator=operator,
                                        n_shots=n_shots, configs=configs)

        ###
        ### Convert the operator format to the Web API-acceptable one
        ###
        if isinstance(operator, ObjectReference):
            api_operator = operator
        else:
            api_operator = to_api_operator(operator)

        ###
        ### Use raw/ref for parameter values that can be large-sized, and upload large-sized parameter values to the cloud
        ###
        ref_able_params_with_none: dict[str, list[Any] | ObjectReference | None] = {
            'code': serialized_code, 'operator': api_operator, 'n_shots': n_shots,
            'parameter_values': parameter_values, 'qubit_allocation': qubit_allocation
        }
        ref_able_params: dict[str, list[Any] | ObjectReference] = remove_none_values(ref_able_params_with_none)

        auto_ref_key = Task._generate_auto_ref_key('param_values')
        param_values_to_upload = {}
        ref_able_param_names = list(ref_able_params.keys())
        for param in ref_able_param_names:
            value = ref_able_params[param]
            if isinstance(value, ObjectReference):
                ref_able_params[param] = {'ref': value.key + StorageService._OBJECT_EXT}
            elif _should_submit_as_raw(param, value):
                ref_able_params[param] = {'raw': value}
            else:
                param_values_to_upload[param] = value
                ref_able_params[param] = {'ref': auto_ref_key + StorageService._OBJECT_EXT}

        if param_values_to_upload:
            StorageService._upload({auto_ref_key: param_values_to_upload}, validation_for_users=False, normalization=False)

        # store qubit_allocation under 'configs'
        qubit_allocation_raw_ref = ref_able_params.pop('qubit_allocation', None)
        if qubit_allocation_raw_ref is not None:
            configs['qubit_allocation'] = qubit_allocation_raw_ref

        ###
        ### Construct a request body for POST /tasks
        ###
        body: dict[str, Any] = {
            "device": device.device_id,
            "type": task_type,
            "method": method,
            "name": name,
            "note": note,
            "configs": snake_to_camel_keys(configs),
        }

        body.update(snake_to_camel_keys(ref_able_params))

        # remove None values
        body = remove_none_values(body)

        # To make the return values be the same as the data sent to the Web API, convert the kay names into camel case
        return body, snake_to_camel_keys(param_values_to_upload)

    @staticmethod
    def _generate_auto_ref_key(object_name: str) -> str:
        return '_/{0}/{1}/{2}'.format(datetime.now(tz=timezone.utc).strftime('%Y/%m/%d'), str(uuid4()), object_name)

    @staticmethod
    def _raise_invalid_param_value_error(condition, param_name, param_value=None):
        if param_value is None:
            raise ValueError(f'{param_name} cannot be specified {condition}')

        raise ValueError(f'{param_name}={param_value} cannot be specified {condition}')

    @staticmethod
    def _validate_parameter_values(device, task_type, method, operator, n_shots, configs):
        # Device-specific validations
        if Task._is_qpu(device):
            if method == Task.EstimationMethod.STATE_VECTOR:
                Task._raise_invalid_param_value_error('for QPU devices', 'method', 'state_vector')

            prohibited_params = ['n_nodes', 'n_per_node', 'seed_simulation']
            for pp in prohibited_params:
                if pp in configs:
                    Task._raise_invalid_param_value_error('for QPU devices', pp)

        else:  # device type == simulator
            prohibited_params = ['qubit_allocation', 'ro_error_mitigation', 'estimation_dop']
            for pp in prohibited_params:
                if pp in configs:
                    Task._raise_invalid_param_value_error('for simulator devices', pp)

        # Task type-specific validations
        if task_type == Task.Type.SAMPLING:
            if method is not None:
                Task._raise_invalid_param_value_error('for sampling tasks', 'method')
            if operator is not None:
                Task._raise_invalid_param_value_error('for sampling tasks', 'operator')
        else:  # task type == estimation
            if method == Task.EstimationMethod.STATE_VECTOR and n_shots is not None:
                Task._raise_invalid_param_value_error('if method==state_vector', 'n_shots')

        # Transpilation-specific validations
        if configs['skip_transpilation']:
            if 'transpilation_options' in configs:
                Task._raise_invalid_param_value_error('if skip_transpilation=True', 'transpilation_options')
            if 'seed_transpilation' in configs:
                Task._raise_invalid_param_value_error('if skip_transpilation=True', 'seed_transpilation')

        # TODO validate parameter values

    def __init__(self,
                 task_def: dict[str, Any]):

        ref_cache: dict[str, dict[str, Any]] = {}  # key: presigned-url, value: a dict of parameter names and values
        single_value_params = []
        if 'configs' in task_def:
            single_value_params = task_def['configs'].pop('sdkSingleValueParams', [])

        self._task_id: UUID = UUID(task_def['taskId'])
        self._device_id: str = task_def['device']
        self._type: Task.Type = Task.Type(task_def['type'])
        self._code: Union[str, list[str], ObjectReference] = resolve_raw_ref('code', task_def.get('code', None), ref_cache)
        if not isinstance(self._code, ObjectReference) and 'code' in single_value_params:
            self._code = to_single_value('code', self._code)

        self._code_paths: Optional[Union[str, PathLike]] = resolve_raw_ref('code_paths', task_def.get('codePaths', None), ref_cache)

        self._n_shots: Optional[Union[int, list[int], ObjectReference]] = resolve_raw_ref('n_shots', task_def.get('nShots', None), ref_cache)
        if not isinstance(self._n_shots, ObjectReference) and 'n_shots' in single_value_params:
            self._n_shots = to_single_value('n_shots', self._n_shots)

        self._method: Optional[Task.EstimationMethod] = Task.EstimationMethod(task_def['method']) if 'method' in task_def else None

        op = resolve_raw_ref('operator', task_def.get('operator', None), ref_cache)
        if not isinstance(op, ObjectReference):
            op = to_sdk_operator(op)
        self._operator: Optional[Union[Operator, list[Operator], ObjectReference]] = op
        if not isinstance(self._operator, ObjectReference) and 'operator' in single_value_params:
            self._operator = to_single_value('operator', self._operator)

        self._parameter_values: Optional[Union[ParameterValues, list[ParameterValues], ObjectReference]]\
            = resolve_raw_ref('parameter_values', task_def.get('parameterValues', None), ref_cache)
        if not isinstance(self._parameter_values, ObjectReference) and 'parameter_values' in single_value_params:
            self._parameter_values = to_single_value('parameter_values', self._parameter_values)

        self._config_path: Optional[Union[str, PathLike]] = resolve_raw_ref('config_path', task_def.get('configPath', None), ref_cache)

        self._status: Task.Status = Task.Status(task_def['status'])
        self._created_at: datetime = datetime.strptime(task_def['createdAt'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)

        self._name: Optional[str] = task_def.get('name', None)
        self._note: Optional[str] = task_def.get('note', None)

        self._configs: dict[str, Any] = {}
        if 'configs' in task_def:
            configs: dict[str, Any] = task_def['configs']
            if 'qubitAllocation' in configs:
                qubit_allocation = resolve_raw_ref('qubit_allocation', configs['qubitAllocation'], ref_cache)
                if not isinstance(qubit_allocation, ObjectReference) and 'qubit_allocation' in single_value_params:
                    configs['qubitAllocation'] = to_single_value('qubit_allocation', qubit_allocation)
                else:
                    configs['qubitAllocation'] = qubit_allocation

            self._configs = camel_to_snake_keys(configs)

        self._result: Optional[Result] = None

    @property
    def task_id(self) -> UUID:
        return self._task_id

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def parameter_values(self) -> Optional[Union[ParameterValues, list[ParameterValues], ObjectReference]]:
        return self._parameter_values

    @property
    def program(self) -> Optional[Union[str, list[str], ObjectReference]]:
        return self._code

    @property
    def program_paths(self) -> Optional[Union[str, PathLike]]:
        return self._code_paths

    @property
    def config_path(self) -> Optional[Union[str, PathLike]]:
        return self._config_path

    @property
    def type(self) -> Type:
        return self._type

    @property
    def n_shots(self) -> Optional[Union[int, list[int], ObjectReference]]:
        return self._n_shots

    @property
    def method(self):
        return self._method

    @property
    def operator(self) -> Optional[Union[Operator, list[Operator], ObjectReference]]:
        return self._operator

    @property
    def status(self) -> Status:
        if (self._status not in [Task.Status.COMPLETED,
                                 Task.Status.FAILED,
                                 Task.Status.CANCELLED]):
            self._status = Task.Status(get_task(self._task_id, {'status'})['status'])

        return self._status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def note(self) -> Optional[str]:
        return self._note

    @property
    def skip_transpilation(self) -> bool:
        return self._configs.get('skip_transpilation', False)

    @property
    def seed_transpilation(self) -> Optional[int]:
        return self._configs.get('seed_transpilation', None)

    @property
    def transpilation_options(self) -> Optional[dict[str, Any]]:
        return self._configs.get('transpilation_options', None)

    @property
    def qubit_allocation(self) -> Optional[Union[QubitAllocation, list[QubitAllocation], ObjectReference]]:
        return self._configs.get('qubit_allocation', None)

    @property
    def ro_error_mitigation(self) -> Optional[Task.ROErrorMitigation]:
        return self._configs.get('ro_error_mitigation', None)

    @property
    def n_nodes(self) -> Optional[int]:
        return self._configs.get('n_nodes', None)

    @property
    def n_per_node(self) -> Optional[int]:
        return self._configs.get('n_per_node', None)

    @property
    def seed_simulation(self) -> Optional[int]:
        return self._configs.get('seed_simulation', None)

    @property
    def estimation_dop(self) -> Optional[Union[int, str]]:
        return self._configs.get('estimation_dop', None)

    def result(self, polling_interval: Optional[Union[int, float]] = None):
        if (polling_interval is not None) and (polling_interval < 1):
            raise ValueError('polling_interval must be greater than or equal to 1, '
                             f'but {polling_interval} is specified.')

        # the argument 'polling_interval' is used over the config value
        if polling_interval is None:
            actual_polling_interval = Config.result_polling_interval
        else:
            actual_polling_interval = polling_interval

        if self._result is None:
            while (self.status not in [Task.Status.COMPLETED,
                                       Task.Status.FAILED,
                                       Task.Status.CANCELLED]):
                # self.status checks status value in API
                time.sleep(actual_polling_interval)

            outputs = get_task(self._task_id, {'outputs'})['outputs']
            self._result = Result(self, outputs)

        return self._result

    def cancel(self) -> None:
        cancel_task(self._task_id)

    def delete(self) -> None:
        delete_task(self._task_id)

    def __str__(self):
        prop_names = [name for name, val in vars(Task).items() if isinstance(val, property)]
        prop_dict = {prop: getattr(self, prop) for prop in prop_names}
        return pformat(prop_dict)


class Tasks:
    @staticmethod
    def iter(order: str = 'desc', page: int = 1, per_page: int = 10,
             start_time: Optional[datetime] = None, end_time: Optional[datetime] = None,
             query: Optional[str] = None):

        return TaskIterator(order, page, per_page, start_time, end_time, query)

    @staticmethod
    def get(task_id: Union[str, UUID]) -> Task:
        return Task(get_task(task_id))


class TaskIterator:

    page_url_regex = re.compile(r'page=(?P<page>\d+)')

    def __init__(self,
                 order: str = 'desc',
                 page: int = 1,
                 per_page: int = 10,
                 start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None,
                 query: Optional[str] = None):

        if order not in ('desc', 'asc'):
            raise ValueError(f'order must be either "desc" or "asc", but {order} was specified.')
        if page < 1:
            raise ValueError(f'page must be greater than 1, but {page} was specified.')
        if per_page < 1:
            raise ValueError(f'per_page must be greater than 1, but {per_page} was specified.')

        self._url_params = {
            'order': order,
            'page': page,
            'perPage': per_page,
        }
        if start_time is not None:
            self._url_params['startTime'] = start_time.replace(tzinfo=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        if end_time is not None:
            self._url_params['endTime'] = end_time.replace(tzinfo=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        if query is not None and len(query) != 0:
            self._url_params['q'] = query

        self._page_tasks: list[Task] = []
        self._page_tasks_index: int = 0
        self._next_page: Optional[int] = page

    def _fetch_next_page(self):
        self._url_params['page'] = self._next_page
        resp, headers = get_tasks(self._url_params)
        self._page_tasks = [Task(task) for task in resp]
        self._page_tasks_index = 0

        self._next_page = None
        try:
            for entry in reversed(headers['Link'].split(',')):  # The "rel=next" header is placed at last; using reversed(...) improves the efficiency.
                url, rel = tuple(entry.split(';'))
                if rel.find('next') != -1:
                    match = TaskIterator.page_url_regex.search(url)
                    self._next_page = int(match.group('page'))
                    break
        except Exception as e:
            raise RuntimeError(f'{type(e)}. {e}.\n'
                               f'Malformed response from the Quantum Cloud API (GET /tasks).'
                               f' The "Link" header is invalid.\nHeaders:\n{headers}')

    def __iter__(self) -> TaskIterator:
        return self

    def __next__(self) -> Task:
        if self._page_tasks_index < len(self._page_tasks):
            self._page_tasks_index += 1
            return self._page_tasks[self._page_tasks_index - 1]
        else:
            if self._next_page is not None:
                self._fetch_next_page()
                return self.__next__()
            else:
                raise StopIteration
