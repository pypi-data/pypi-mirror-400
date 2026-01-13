import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ApiKey(_message.Message):
    __slots__ = ("id", "name", "key_hint", "scopes", "expires_at", "created_at", "last_used_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    KEY_HINT_FIELD_NUMBER: _ClassVar[int]
    SCOPES_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    LAST_USED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    key_hint: str
    scopes: _containers.RepeatedScalarFieldContainer[str]
    expires_at: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    last_used_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., key_hint: _Optional[str] = ..., scopes: _Optional[_Iterable[str]] = ..., expires_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., last_used_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateApiKeyRequest(_message.Message):
    __slots__ = ("name", "scopes", "expires_in_seconds")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SCOPES_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_IN_SECONDS_FIELD_NUMBER: _ClassVar[int]
    name: str
    scopes: _containers.RepeatedScalarFieldContainer[str]
    expires_in_seconds: int
    def __init__(self, name: _Optional[str] = ..., scopes: _Optional[_Iterable[str]] = ..., expires_in_seconds: _Optional[int] = ...) -> None: ...

class CreateApiKeyResponse(_message.Message):
    __slots__ = ("key", "key_secret")
    KEY_FIELD_NUMBER: _ClassVar[int]
    KEY_SECRET_FIELD_NUMBER: _ClassVar[int]
    key: ApiKey
    key_secret: str
    def __init__(self, key: _Optional[_Union[ApiKey, _Mapping]] = ..., key_secret: _Optional[str] = ...) -> None: ...

class ListApiKeysRequest(_message.Message):
    __slots__ = ("page_size", "page_token")
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    page_size: int
    page_token: str
    def __init__(self, page_size: _Optional[int] = ..., page_token: _Optional[str] = ...) -> None: ...

class ListApiKeysResponse(_message.Message):
    __slots__ = ("keys", "next_page_token")
    KEYS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    keys: _containers.RepeatedCompositeFieldContainer[ApiKey]
    next_page_token: str
    def __init__(self, keys: _Optional[_Iterable[_Union[ApiKey, _Mapping]]] = ..., next_page_token: _Optional[str] = ...) -> None: ...

class RevokeApiKeyRequest(_message.Message):
    __slots__ = ("key_id",)
    KEY_ID_FIELD_NUMBER: _ClassVar[int]
    key_id: str
    def __init__(self, key_id: _Optional[str] = ...) -> None: ...

class RevokeApiKeyResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...
