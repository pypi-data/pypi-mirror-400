from google.api import resource_pb2 as _resource_pb2
from google.api import field_behavior_pb2 as _field_behavior_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TokenSource(_message.Message):
    __slots__ = ("name", "redirect_uri", "login_uri", "login_required", "access_token", "issue_time", "expire_time", "subject", "login_principal", "creator", "create_time", "login_time", "uid")
    NAME_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_URI_FIELD_NUMBER: _ClassVar[int]
    LOGIN_URI_FIELD_NUMBER: _ClassVar[int]
    LOGIN_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ISSUE_TIME_FIELD_NUMBER: _ClassVar[int]
    EXPIRE_TIME_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    LOGIN_PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    CREATOR_FIELD_NUMBER: _ClassVar[int]
    CREATE_TIME_FIELD_NUMBER: _ClassVar[int]
    LOGIN_TIME_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    name: str
    redirect_uri: str
    login_uri: str
    login_required: bool
    access_token: str
    issue_time: _timestamp_pb2.Timestamp
    expire_time: _timestamp_pb2.Timestamp
    subject: str
    login_principal: str
    creator: str
    create_time: _timestamp_pb2.Timestamp
    login_time: _timestamp_pb2.Timestamp
    uid: str
    def __init__(self, name: _Optional[str] = ..., redirect_uri: _Optional[str] = ..., login_uri: _Optional[str] = ..., login_required: bool = ..., access_token: _Optional[str] = ..., issue_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., expire_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., subject: _Optional[str] = ..., login_principal: _Optional[str] = ..., creator: _Optional[str] = ..., create_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., login_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., uid: _Optional[str] = ...) -> None: ...
