# (C) 2025 Fujitsu Limited

import json
from datetime import timezone
from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

from google.protobuf.internal.well_known_types import Timestamp
from requests.structures import CaseInsensitiveDict

from fujitsu_quantum.api.grpc_client import get_stub
from fujitsu_quantum.api.user_pb2 import (CancelTaskRequest, CreateTaskRequest, CreateTaskResponse, GetTaskRequest,
                                          GetTaskResponse, DeleteTaskRequest)
from fujitsu_quantum.config import Config
from fujitsu_quantum.requests import FQCRequest
from fujitsu_quantum.utils import camel_to_snake, remove_none_values, json_dumps

DEVICE_ENDPOINT: str = Config.api_base + '/devices'
TASKS_ENDPOINT: str = Config.api_base + '/tasks'


def get_devices() -> list[dict[str, Any]]:
    return FQCRequest.get(DEVICE_ENDPOINT).json()


def get_device(device_id: str) -> dict[str, Any]:
    return FQCRequest.get(f'{DEVICE_ENDPOINT}/{device_id}').json()


_grpc_create_task_json_encoded_params_in_camel = ['code', 'nShots', 'operator', 'configs']


def _rest_to_grpc_create_task_request(rest_request: dict[str, Any]) -> dict[str, Any]:
    # TODO make parameter_values as a top-level parameter
    has_parameter_values = False
    has_configs = True
    if 'parameterValues' in rest_request:
        has_parameter_values = True
        if 'configs' not in rest_request:
            has_configs = False
            rest_request['configs'] = {}
        rest_request['configs']['parameterValues'] = rest_request.pop('parameterValues')

    grpc_request = {}
    for camel_param, value in rest_request.items():
        grpc_value = value
        if camel_param in _grpc_create_task_json_encoded_params_in_camel:
            grpc_value = json_dumps(value)
        grpc_request[camel_to_snake(camel_param)] = grpc_value

    # revert the move of parameter_values
    if has_parameter_values:
        rest_request['parameterValues'] = rest_request['configs'].pop('parameterValues')
        if not has_configs:
            rest_request.pop('configs')

    return grpc_request


def _grpc_to_rest_datetime(grpc_datetime: Timestamp):
    return grpc_datetime.ToDatetime(tzinfo=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def create_task(parameters: dict[str, Any]) -> dict[str, Any]:
    if Config.in_hybrid_env:
        if parameters['type'] == 'hybrid':
            raise ValueError('Creating another hybrid task within a hybrid task is not allowed.')

        grpc_stub = get_stub()
        grpc_parameters = _rest_to_grpc_create_task_request(parameters)
        resp: CreateTaskResponse = grpc_stub.CreateTask(CreateTaskRequest(**grpc_parameters))
        return {
            'taskId': resp.task_id,
            'status': resp.status,
            'createdAt': _grpc_to_rest_datetime(resp.created_at)
        }
    else:
        return FQCRequest.post(status_code=HTTPStatus.CREATED, url=TASKS_ENDPOINT, data=json_dumps(parameters)).json()


# parameterValues, configs, and createdAt are excluded from the below lists because they need special cares in conversion
_grpc_to_rest_params_in_camel = ['taskId', 'owner', 'name', 'status', 'device', 'code', 'type', 'method',
                                 'nShots', 'operator', 'outputs', 'note']
_grpc_to_rest_params_in_snake = [camel_to_snake(p) for p in _grpc_to_rest_params_in_camel]
_grpc_to_rest_json_encoded_params_in_snake = ['code', 'n_shots', 'operator', 'outputs']


def _grpc_to_rest_response(response: GetTaskResponse) -> dict[str, Any]:
    rest_response = {}
    for camel_param, snake_param in zip(_grpc_to_rest_params_in_camel, _grpc_to_rest_params_in_snake):
        if response.HasField(snake_param):
            value = getattr(response, snake_param)
            if snake_param in _grpc_to_rest_json_encoded_params_in_snake:
                value = json.loads(value)

            rest_response[camel_param] = value

    # move parameterValues to a top-level element in the response dict
    configs = json.loads(response.configs) if response.HasField('configs') else None
    if configs is not None:
        rest_response['configs'] = configs

        param_values = configs.pop('parameterValues', None)
        if param_values is not None:
            rest_response['parameterValues'] = param_values

    if response.HasField('created_at'):
        rest_response['createdAt'] = _grpc_to_rest_datetime(response.created_at)

    return remove_none_values(rest_response)


def get_task(task_id: Union[UUID, str], fields: set[str] = None) -> dict[str, Any]:
    if Config.in_hybrid_env:
        grpc_stub = get_stub()
        if fields is None:
            fields = set()
        resp: GetTaskResponse = grpc_stub.GetTask(GetTaskRequest(task_id=str(task_id), fields=fields))
        return _grpc_to_rest_response(resp)
    else:
        params = {'fields': ','.join(fields)} if fields is not None else None
        return FQCRequest.get(url=f'{TASKS_ENDPOINT}/{str(task_id)}', params=params).json()


def get_tasks(parameters: dict[str, Any] = None) -> tuple[list[dict[str, Any]], CaseInsensitiveDict]:
    # TODO support retrieving primitive tasks submit from the inside of hybrid tasks
    resp = FQCRequest.get(url=TASKS_ENDPOINT, params=parameters)
    return resp.json(), resp.headers


def cancel_task(task_id: UUID):
    if Config.in_hybrid_env:
        grpc_stub = get_stub()
        grpc_stub.CancelTask(CancelTaskRequest(task_id=str(task_id)))
    else:
        FQCRequest.post(status_code=HTTPStatus.OK, url=f'{TASKS_ENDPOINT}/{str(task_id)}/cancel')


def delete_task(task_id: UUID):
    if Config.in_hybrid_env:
        grpc_stub = get_stub()
        grpc_stub.DeleteTask(DeleteTaskRequest(task_id=str(task_id)))
    else:
        FQCRequest.delete(url=f'{TASKS_ENDPOINT}/{str(task_id)}')
