from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.api import resource_pb2 as _resource_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OAuthClient(_message.Message):
    __slots__ = ("name", "display_name", "issuer", "client_id", "client_secret", "client_secret_set", "authorization_endpoint", "token_endpoint", "extra_scopes", "refresh_disabled", "login_principal_claim", "callback_uri", "creator", "updater", "create_time", "update_time", "uid")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_SECRET_FIELD_NUMBER: _ClassVar[int]
    CLIENT_SECRET_SET_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    TOKEN_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    EXTRA_SCOPES_FIELD_NUMBER: _ClassVar[int]
    REFRESH_DISABLED_FIELD_NUMBER: _ClassVar[int]
    LOGIN_PRINCIPAL_CLAIM_FIELD_NUMBER: _ClassVar[int]
    CALLBACK_URI_FIELD_NUMBER: _ClassVar[int]
    CREATOR_FIELD_NUMBER: _ClassVar[int]
    UPDATER_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    UPDATE_TIME_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    name: str
    display_name: str
    issuer: str
    client_id: str
    client_secret: str
    client_secret_set: bool
    authorization_endpoint: str
    token_endpoint: str
    extra_scopes: _containers.RepeatedScalarFieldContainer[str]
    refresh_disabled: bool
    login_principal_claim: str
    callback_uri: str
    creator: str
    updater: str
    create_time: _timestamp_pb2.Timestamp
    update_time: _timestamp_pb2.Timestamp
    uid: str
    def __init__(self, name: _Optional[str] = ..., display_name: _Optional[str] = ..., issuer: _Optional[str] = ..., client_id: _Optional[str] = ..., client_secret: _Optional[str] = ..., client_secret_set: bool = ..., authorization_endpoint: _Optional[str] = ..., token_endpoint: _Optional[str] = ..., extra_scopes: _Optional[_Iterable[str]] = ..., refresh_disabled: bool = ..., login_principal_claim: _Optional[str] = ..., callback_uri: _Optional[str] = ..., creator: _Optional[str] = ..., updater: _Optional[str] = ..., create_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., update_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., uid: _Optional[str] = ...) -> None: ...
