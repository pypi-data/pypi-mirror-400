from google.protobuf import empty_pb2 as _empty_pb2
from google.rpc import status_pb2 as _status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProtocolRevision(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REVISION_ZERO: _ClassVar[ProtocolRevision]
    REVISION_ONE: _ClassVar[ProtocolRevision]
REVISION_ZERO: ProtocolRevision
REVISION_ONE: ProtocolRevision

class ClientToServer(_message.Message):
    __slots__ = ("stream_id", "new_stream", "request_message", "more_request_data", "half_close", "cancel", "window_update")
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    NEW_STREAM_FIELD_NUMBER: _ClassVar[int]
    REQUEST_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    MORE_REQUEST_DATA_FIELD_NUMBER: _ClassVar[int]
    HALF_CLOSE_FIELD_NUMBER: _ClassVar[int]
    CANCEL_FIELD_NUMBER: _ClassVar[int]
    WINDOW_UPDATE_FIELD_NUMBER: _ClassVar[int]
    stream_id: int
    new_stream: NewStream
    request_message: MessageData
    more_request_data: bytes
    half_close: _empty_pb2.Empty
    cancel: _empty_pb2.Empty
    window_update: int
    def __init__(self, stream_id: _Optional[int] = ..., new_stream: _Optional[_Union[NewStream, _Mapping]] = ..., request_message: _Optional[_Union[MessageData, _Mapping]] = ..., more_request_data: _Optional[bytes] = ..., half_close: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., cancel: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ..., window_update: _Optional[int] = ...) -> None: ...

class ServerToClient(_message.Message):
    __slots__ = ("stream_id", "settings", "response_headers", "response_message", "more_response_data", "close_stream", "window_update")
    STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_HEADERS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    MORE_RESPONSE_DATA_FIELD_NUMBER: _ClassVar[int]
    CLOSE_STREAM_FIELD_NUMBER: _ClassVar[int]
    WINDOW_UPDATE_FIELD_NUMBER: _ClassVar[int]
    stream_id: int
    settings: Settings
    response_headers: Metadata
    response_message: MessageData
    more_response_data: bytes
    close_stream: CloseStream
    window_update: int
    def __init__(self, stream_id: _Optional[int] = ..., settings: _Optional[_Union[Settings, _Mapping]] = ..., response_headers: _Optional[_Union[Metadata, _Mapping]] = ..., response_message: _Optional[_Union[MessageData, _Mapping]] = ..., more_response_data: _Optional[bytes] = ..., close_stream: _Optional[_Union[CloseStream, _Mapping]] = ..., window_update: _Optional[int] = ...) -> None: ...

class Settings(_message.Message):
    __slots__ = ("supported_protocol_revisions", "initial_window_size")
    SUPPORTED_PROTOCOL_REVISIONS_FIELD_NUMBER: _ClassVar[int]
    INITIAL_WINDOW_SIZE_FIELD_NUMBER: _ClassVar[int]
    supported_protocol_revisions: _containers.RepeatedScalarFieldContainer[ProtocolRevision]
    initial_window_size: int
    def __init__(self, supported_protocol_revisions: _Optional[_Iterable[_Union[ProtocolRevision, str]]] = ..., initial_window_size: _Optional[int] = ...) -> None: ...

class NewStream(_message.Message):
    __slots__ = ("method_name", "request_headers", "initial_window_size", "protocol_revision")
    METHOD_NAME_FIELD_NUMBER: _ClassVar[int]
    REQUEST_HEADERS_FIELD_NUMBER: _ClassVar[int]
    INITIAL_WINDOW_SIZE_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_REVISION_FIELD_NUMBER: _ClassVar[int]
    method_name: str
    request_headers: Metadata
    initial_window_size: int
    protocol_revision: ProtocolRevision
    def __init__(self, method_name: _Optional[str] = ..., request_headers: _Optional[_Union[Metadata, _Mapping]] = ..., initial_window_size: _Optional[int] = ..., protocol_revision: _Optional[_Union[ProtocolRevision, str]] = ...) -> None: ...

class MessageData(_message.Message):
    __slots__ = ("size", "data")
    SIZE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    size: int
    data: bytes
    def __init__(self, size: _Optional[int] = ..., data: _Optional[bytes] = ...) -> None: ...

class CloseStream(_message.Message):
    __slots__ = ("response_trailers", "status")
    RESPONSE_TRAILERS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    response_trailers: Metadata
    status: _status_pb2.Status
    def __init__(self, response_trailers: _Optional[_Union[Metadata, _Mapping]] = ..., status: _Optional[_Union[_status_pb2.Status, _Mapping]] = ...) -> None: ...

class Metadata(_message.Message):
    __slots__ = ("md",)
    class Values(_message.Message):
        __slots__ = ("val",)
        VAL_FIELD_NUMBER: _ClassVar[int]
        val: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, val: _Optional[_Iterable[str]] = ...) -> None: ...
    class MdEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Metadata.Values
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Metadata.Values, _Mapping]] = ...) -> None: ...
    MD_FIELD_NUMBER: _ClassVar[int]
    md: _containers.MessageMap[str, Metadata.Values]
    def __init__(self, md: _Optional[_Mapping[str, Metadata.Values]] = ...) -> None: ...
