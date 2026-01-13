from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateTaskRequest(_message.Message):
    __slots__ = ("name", "device", "code", "type", "method", "n_shots", "operator", "configs", "note")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    N_SHOTS_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    CONFIGS_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    name: str
    device: str
    code: str
    type: str
    method: str
    n_shots: str
    operator: str
    configs: str
    note: str
    def __init__(self, name: _Optional[str] = ..., device: _Optional[str] = ..., code: _Optional[str] = ..., type: _Optional[str] = ..., method: _Optional[str] = ..., n_shots: _Optional[str] = ..., operator: _Optional[str] = ..., configs: _Optional[str] = ..., note: _Optional[str] = ...) -> None: ...

class CreateTaskResponse(_message.Message):
    __slots__ = ("task_id", "created_at", "status")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    created_at: _timestamp_pb2.Timestamp
    status: str
    def __init__(self, task_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., status: _Optional[str] = ...) -> None: ...

class CancelTaskRequest(_message.Message):
    __slots__ = ("task_id",)
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    def __init__(self, task_id: _Optional[str] = ...) -> None: ...

class CancelTaskResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DeleteTaskRequest(_message.Message):
    __slots__ = ("task_id",)
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    def __init__(self, task_id: _Optional[str] = ...) -> None: ...

class DeleteTaskResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetTaskRequest(_message.Message):
    __slots__ = ("task_id", "fields")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    fields: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, task_id: _Optional[str] = ..., fields: _Optional[_Iterable[str]] = ...) -> None: ...

class GetTaskResponse(_message.Message):
    __slots__ = ("task_id", "owner", "name", "status", "created_at", "device", "code", "type", "method", "n_shots", "operator", "configs", "outputs", "note")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    DEVICE_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    N_SHOTS_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    CONFIGS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    NOTE_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    owner: str
    name: str
    status: str
    created_at: _timestamp_pb2.Timestamp
    device: str
    code: str
    type: str
    method: str
    n_shots: str
    operator: str
    configs: str
    outputs: str
    note: str
    def __init__(self, task_id: _Optional[str] = ..., owner: _Optional[str] = ..., name: _Optional[str] = ..., status: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., device: _Optional[str] = ..., code: _Optional[str] = ..., type: _Optional[str] = ..., method: _Optional[str] = ..., n_shots: _Optional[str] = ..., operator: _Optional[str] = ..., configs: _Optional[str] = ..., outputs: _Optional[str] = ..., note: _Optional[str] = ...) -> None: ...
