from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GetIdRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetIdResponse(_message.Message):
    __slots__ = ()
    ID_FIELD_NUMBER: _ClassVar[int]
    HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    id: str
    hostname: str
    def __init__(self, id: _Optional[str] = ..., hostname: _Optional[str] = ...) -> None: ...

class GetTimeRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetTimeResponse(_message.Message):
    __slots__ = ()
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    FORMATTED_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    formatted: str
    timezone: str
    def __init__(self, timestamp: _Optional[int] = ..., formatted: _Optional[str] = ..., timezone: _Optional[str] = ...) -> None: ...
