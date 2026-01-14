from h2o_secure_store.gen.ai.h2o.securestore.v1 import oauth_client_pb2 as _oauth_client_pb2
from google.api import annotations_pb2 as _annotations_pb2
from google.api import resource_pb2 as _resource_pb2
from google.api import client_pb2 as _client_pb2
from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf import field_mask_pb2 as _field_mask_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateOAuthClientRequest(_message.Message):
    __slots__ = ("oauth_client", "oauth_client_id")
    OAUTH_CLIENT_FIELD_NUMBER: _ClassVar[int]
    OAUTH_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    oauth_client: _oauth_client_pb2.OAuthClient
    oauth_client_id: str
    def __init__(self, oauth_client: _Optional[_Union[_oauth_client_pb2.OAuthClient, _Mapping]] = ..., oauth_client_id: _Optional[str] = ...) -> None: ...

class CreateOAuthClientResponse(_message.Message):
    __slots__ = ("oauth_client",)
    OAUTH_CLIENT_FIELD_NUMBER: _ClassVar[int]
    oauth_client: _oauth_client_pb2.OAuthClient
    def __init__(self, oauth_client: _Optional[_Union[_oauth_client_pb2.OAuthClient, _Mapping]] = ...) -> None: ...

class GetOAuthClientRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class GetOAuthClientResponse(_message.Message):
    __slots__ = ("oauth_client",)
    OAUTH_CLIENT_FIELD_NUMBER: _ClassVar[int]
    oauth_client: _oauth_client_pb2.OAuthClient
    def __init__(self, oauth_client: _Optional[_Union[_oauth_client_pb2.OAuthClient, _Mapping]] = ...) -> None: ...

class ListOAuthClientsRequest(_message.Message):
    __slots__ = ("page_size", "page_token")
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    page_size: int
    page_token: str
    def __init__(self, page_size: _Optional[int] = ..., page_token: _Optional[str] = ...) -> None: ...

class ListOAuthClientsResponse(_message.Message):
    __slots__ = ("oauth_clients", "next_page_token")
    OAUTH_CLIENTS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    oauth_clients: _containers.RepeatedCompositeFieldContainer[_oauth_client_pb2.OAuthClient]
    next_page_token: str
    def __init__(self, oauth_clients: _Optional[_Iterable[_Union[_oauth_client_pb2.OAuthClient, _Mapping]]] = ..., next_page_token: _Optional[str] = ...) -> None: ...

class UpdateOAuthClientRequest(_message.Message):
    __slots__ = ("oauth_client", "update_mask")
    OAUTH_CLIENT_FIELD_NUMBER: _ClassVar[int]
    UPDATE_MASK_FIELD_NUMBER: _ClassVar[int]
    oauth_client: _oauth_client_pb2.OAuthClient
    update_mask: _field_mask_pb2.FieldMask
    def __init__(self, oauth_client: _Optional[_Union[_oauth_client_pb2.OAuthClient, _Mapping]] = ..., update_mask: _Optional[_Union[_field_mask_pb2.FieldMask, _Mapping]] = ...) -> None: ...

class UpdateOAuthClientResponse(_message.Message):
    __slots__ = ("oauth_client",)
    OAUTH_CLIENT_FIELD_NUMBER: _ClassVar[int]
    oauth_client: _oauth_client_pb2.OAuthClient
    def __init__(self, oauth_client: _Optional[_Union[_oauth_client_pb2.OAuthClient, _Mapping]] = ...) -> None: ...

class DeleteOAuthClientRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class DeleteOAuthClientResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class InvalidateTokenSourcesRequest(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class InvalidateTokenSourcesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
