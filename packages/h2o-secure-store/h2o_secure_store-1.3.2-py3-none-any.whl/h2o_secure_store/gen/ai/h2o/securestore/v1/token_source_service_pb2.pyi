from h2o_secure_store.gen.ai.h2o.securestore.v1 import token_source_pb2 as _token_source_pb2
from google.api import annotations_pb2 as _annotations_pb2
from google.api import resource_pb2 as _resource_pb2
from google.api import client_pb2 as _client_pb2
from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateTokenSourceRequest(_message.Message):
    __slots__ = ("parent", "token_source", "token_source_id")
    PARENT_FIELD_NUMBER: _ClassVar[int]
    TOKEN_SOURCE_FIELD_NUMBER: _ClassVar[int]
    TOKEN_SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    parent: str
    token_source: _token_source_pb2.TokenSource
    token_source_id: str
    def __init__(self, parent: _Optional[str] = ..., token_source: _Optional[_Union[_token_source_pb2.TokenSource, _Mapping]] = ..., token_source_id: _Optional[str] = ...) -> None: ...

class CreateTokenSourceResponse(_message.Message):
    __slots__ = ("token_source",)
    TOKEN_SOURCE_FIELD_NUMBER: _ClassVar[int]
    token_source: _token_source_pb2.TokenSource
    def __init__(self, token_source: _Optional[_Union[_token_source_pb2.TokenSource, _Mapping]] = ...) -> None: ...

class GetTokenSourceRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class GetTokenSourceResponse(_message.Message):
    __slots__ = ("token_source",)
    TOKEN_SOURCE_FIELD_NUMBER: _ClassVar[int]
    token_source: _token_source_pb2.TokenSource
    def __init__(self, token_source: _Optional[_Union[_token_source_pb2.TokenSource, _Mapping]] = ...) -> None: ...

class ListTokenSourcesRequest(_message.Message):
    __slots__ = ("parent", "page_size", "page_token")
    PARENT_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    parent: str
    page_size: int
    page_token: str
    def __init__(self, parent: _Optional[str] = ..., page_size: _Optional[int] = ..., page_token: _Optional[str] = ...) -> None: ...

class ListTokenSourcesResponse(_message.Message):
    __slots__ = ("token_sources", "next_page_token")
    TOKEN_SOURCES_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    token_sources: _containers.RepeatedCompositeFieldContainer[_token_source_pb2.TokenSource]
    next_page_token: str
    def __init__(self, token_sources: _Optional[_Iterable[_Union[_token_source_pb2.TokenSource, _Mapping]]] = ..., next_page_token: _Optional[str] = ...) -> None: ...

class DeleteTokenSourceRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class DeleteTokenSourceResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
