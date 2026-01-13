# (C) 2024 Fujitsu Limited

import datetime
import traceback
from http import HTTPStatus
from typing import Any, Dict, Optional, Union

from requests import HTTPError, RequestException, Response

from fujitsu_quantum import logging
from fujitsu_quantum.auth import FQCAuthError
from fujitsu_quantum.config import Config
from fujitsu_quantum.session import AuthType, get_session


class RequestError(Exception):
    """
    Attributes:
        code: Response status code. It can be None if, for example, network errors occur.
        message: Error message.
    """

    def __init__(self, code, message):
        super().__init__(code, message)
        self.code = code
        self.message = message

    def __str__(self):
        if self.code is None:
            return self.message
        else:
            return f'HTTP {self.code}: {self.message}'


class Request:

    @staticmethod
    def _write_error_log(e: Union[RequestException, Exception], additional_info: Optional[str] = None) -> str:
        """Writes the error details to an error log file.

        Returns:
            str: The error log file path.
        """

        err_msg_header = f'RequestError occurred at {str(datetime.datetime.now(datetime.timezone.utc))} UTC. \
                          \n----------------------------\n'

        err_msg = ''
        if isinstance(e, RequestException):
            request = e.request
            if request is None:
                err_msg += 'Request: None\n----------------------------\n'
            else:
                err_msg += (f'Request: {request.method} {request.url}\n----------------------------\n'
                            f'Request header: {request.headers}\n----------------------------\n')
                if hasattr(request, 'body'):
                    err_msg += f'Request body: {str(request.body)}\n----------------------------\n'

            response = e.response
            if response is None:
                err_msg += 'Response: None\n----------------------------\n'
            else:
                err_msg += (f'Response status code: {response.status_code}\n----------------------------\n'
                            f'Response header: {response.headers}\n----------------------------\n'
                            f'Response body: {response.text}\n----------------------------\n')

        if additional_info is not None:
            err_msg += f'Additional info: {additional_info}\n----------------------------\n'

        exception_details = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        err_msg += f'Exception info: \n{exception_details}\n'

        return logging.write_error_log(f'{err_msg_header}{err_msg}')

    @staticmethod
    def __request(method: str, auth_type: AuthType, exp_status_code: HTTPStatus, **kwargs: Any) -> Response:
        """
        Parameters:
            method (str): HTTP method to use.
            exp_status_code (HTTPStatus): expected HTTP response status code.
            kwargs (Any): Additional parameters to pass to requests.
        """

        if 'timeout' not in kwargs:
            kwargs['timeout'] = (Config.connect_timeout, Config.read_timeout)

        # TODO Re-design the SDK entirely to support Session instead of creating a new session every time.
        #  Notice: Session is not process-safe. Do not share one Session object among multi-processes.
        session = get_session(auth_type=auth_type)
        try:
            resp: Response = getattr(session, method)(**kwargs)
        except FQCAuthError:
            # This error occurs if, e.g., refresh token has been expired
            # re-throw
            raise
        except Exception as e:
            # e.g., a too-many-redirections error comes into this clause
            log_file_path = Request._write_error_log(e)
            request_path = method.upper() + ' ' + kwargs.get('url', 'unknown URL')
            raise RequestError(None, f'Request failed: {request_path}\n'
                                     f'Error details have been saved to {log_file_path}')
        else:
            try:
                # In addition to checking the response status code against the expected one,
                # call raise_for_status() to construct a better error message for a 4xx or 5xx response.
                resp.raise_for_status()
                if resp.status_code != exp_status_code:
                    raise HTTPError(f'Unexpected HTTP response code (expected {exp_status_code},'
                                    f' but got {resp.status_code}) for url {resp.url}', response=resp)

                return resp
            except RequestException as e:  # this clause catches HTTPError
                log_file_path = Request._write_error_log(e)
                request_path = method.upper() + ' ' + kwargs.get('url', 'unknown URL')
                if (resp.headers.get('Content-Type', '').startswith('application/json')) and 'error' in resp.json():
                    response_err_msg = resp.json()['error']
                else:
                    response_err_msg = resp.text
                err_msg = (f'Request failed: {request_path}\n'
                           f'{response_err_msg}\n'
                           f'Error details have been saved to {log_file_path}')
                raise RequestError(resp.status_code, err_msg) from None

    @staticmethod
    def get(auth_type: AuthType = AuthType.NONE, exp_status_code: HTTPStatus = HTTPStatus.OK, **kwargs: Any):
        if 'params' in kwargs and kwargs['params'] is None:
            kwargs.pop('params')

        return Request.__request('get', auth_type=auth_type, exp_status_code=exp_status_code, **kwargs)

    @staticmethod
    def post(auth_type: AuthType = AuthType.NONE, exp_status_code: HTTPStatus = HTTPStatus.OK, **kwargs: Any):
        return Request.__request('post', auth_type=auth_type, exp_status_code=exp_status_code, **kwargs)

    @staticmethod
    def delete(auth_type: AuthType = AuthType.NONE, exp_status_code: HTTPStatus = HTTPStatus.OK, **kwargs: Any):
        return Request.__request('delete', auth_type=auth_type, exp_status_code=exp_status_code, **kwargs)


class FQCRequest:

    @staticmethod
    def get(url: str, params: Optional[Dict[str, Any]] = None):
        return Request.get(auth_type=AuthType.FQC, exp_status_code=HTTPStatus.OK, url=url, params=params)

    @staticmethod
    def post(status_code: HTTPStatus, url: str, data: str = ''):
        return Request.post(auth_type=AuthType.FQC, exp_status_code=status_code, url=url, data=data)

    @staticmethod
    def delete(url: str):
        return Request.delete(auth_type=AuthType.FQC, exp_status_code=HTTPStatus.NO_CONTENT, url=url)
