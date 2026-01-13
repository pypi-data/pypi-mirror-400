from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class EdgeAliveRequest(_message.Message):
    __slots__ = ()
    class MetadataEntry(_message.Message):
        __slots__ = ()
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    EDGE_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    edge_id: str
    timestamp: int
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, edge_id: _Optional[str] = ..., timestamp: _Optional[int] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class EdgeAliveResponse(_message.Message):
    __slots__ = ()
    ACKNOWLEDGED_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    acknowledged: bool
    message: str
    def __init__(self, acknowledged: _Optional[bool] = ..., message: _Optional[str] = ...) -> None: ...

class EdgeGoingAwayRequest(_message.Message):
    __slots__ = ()
    EDGE_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    edge_id: str
    reason: str
    def __init__(self, edge_id: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

class EdgeGoingAwayResponse(_message.Message):
    __slots__ = ()
    ACKNOWLEDGED_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    acknowledged: bool
    message: str
    def __init__(self, acknowledged: _Optional[bool] = ..., message: _Optional[str] = ...) -> None: ...
