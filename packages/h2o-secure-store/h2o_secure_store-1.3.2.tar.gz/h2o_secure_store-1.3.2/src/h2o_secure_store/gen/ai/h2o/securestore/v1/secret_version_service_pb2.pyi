from h2o_secure_store.gen.ai.h2o.securestore.v1 import secret_version_pb2 as _secret_version_pb2
from google.api import annotations_pb2 as _annotations_pb2
from google.api import resource_pb2 as _resource_pb2
from google.api import client_pb2 as _client_pb2
from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateSecretVersionRequest(_message.Message):
    __slots__ = ("parent", "secret_version")
    PARENT_FIELD_NUMBER: _ClassVar[int]
    SECRET_VERSION_FIELD_NUMBER: _ClassVar[int]
    parent: str
    secret_version: _secret_version_pb2.SecretVersion
    def __init__(self, parent: _Optional[str] = ..., secret_version: _Optional[_Union[_secret_version_pb2.SecretVersion, _Mapping]] = ...) -> None: ...

class CreateSecretVersionResponse(_message.Message):
    __slots__ = ("secret_version",)
    SECRET_VERSION_FIELD_NUMBER: _ClassVar[int]
    secret_version: _secret_version_pb2.SecretVersion
    def __init__(self, secret_version: _Optional[_Union[_secret_version_pb2.SecretVersion, _Mapping]] = ...) -> None: ...

class GetSecretVersionRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class GetSecretVersionResponse(_message.Message):
    __slots__ = ("secret_version",)
    SECRET_VERSION_FIELD_NUMBER: _ClassVar[int]
    secret_version: _secret_version_pb2.SecretVersion
    def __init__(self, secret_version: _Optional[_Union[_secret_version_pb2.SecretVersion, _Mapping]] = ...) -> None: ...

class ListSecretVersionsRequest(_message.Message):
    __slots__ = ("parent", "page_size", "page_token")
    PARENT_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    parent: str
    page_size: int
    page_token: str
    def __init__(self, parent: _Optional[str] = ..., page_size: _Optional[int] = ..., page_token: _Optional[str] = ...) -> None: ...

class ListSecretVersionsResponse(_message.Message):
    __slots__ = ("secret_versions", "next_page_token", "total_size")
    SECRET_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SIZE_FIELD_NUMBER: _ClassVar[int]
    secret_versions: _containers.RepeatedCompositeFieldContainer[_secret_version_pb2.SecretVersion]
    next_page_token: str
    total_size: int
    def __init__(self, secret_versions: _Optional[_Iterable[_Union[_secret_version_pb2.SecretVersion, _Mapping]]] = ..., next_page_token: _Optional[str] = ..., total_size: _Optional[int] = ...) -> None: ...

class RevealSecretVersionValueRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class RevealSecretVersionValueResponse(_message.Message):
    __slots__ = ("name", "value")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: bytes
    def __init__(self, name: _Optional[str] = ..., value: _Optional[bytes] = ...) -> None: ...
