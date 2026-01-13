# (C) 2025 Fujitsu Limited

import os
import threading
from functools import lru_cache

import grpc
from grpc import UnaryUnaryClientInterceptor, StatusCode

from fujitsu_quantum.api.user_pb2_grpc import UserAPIStub
from fujitsu_quantum.config import Config
from fujitsu_quantum.utils import json_dumps

_service_config_json =  json_dumps(
    {
        "methodConfig": [
            {
                "name": [{}],  # apply retry to all methods
                "retryPolicy": {
                    "maxAttempts": 5,
                    "initialBackoff": '0.1s',
                    "maxBackoff": '1s',
                    "backoffMultiplier": 2,
                    "retryableStatusCodes": [
                        StatusCode.UNKNOWN.name,
                        StatusCode.DEADLINE_EXCEEDED.name,
                        StatusCode.RESOURCE_EXHAUSTED.name,
                        StatusCode.INTERNAL.name,
                        StatusCode.UNAVAILABLE.name,
                        StatusCode.DATA_LOSS.name,
                    ],
                },
            }
        ]
    })


_default_options = [
    ("grpc.enable_retries", 1),
    ("grpc.service_config", _service_config_json),
]


class AuthInterceptor(UnaryUnaryClientInterceptor):
    def __init__(self, token: str):
        self._token = token

    def intercept_unary_unary(self, continuation, client_call_details, request):
        metadata = client_call_details.metadata or []
        metadata = list(metadata) + [("authorization", f"Bearer {self._token}")]
        client_call_details = client_call_details._replace(metadata=metadata)
        return continuation(client_call_details, request)


@lru_cache
def _get_stub(pid: int, thread_id: int) -> UserAPIStub:
    auth_interceptor = AuthInterceptor(Config.internal_api_token)

    channel = grpc.insecure_channel(Config.internal_api_server, options=_default_options)
    intercept_channel = grpc.intercept_channel(channel, auth_interceptor)
    return UserAPIStub(intercept_channel)


def get_stub() -> UserAPIStub:
    return _get_stub(os.getpid(), threading.get_ident())
