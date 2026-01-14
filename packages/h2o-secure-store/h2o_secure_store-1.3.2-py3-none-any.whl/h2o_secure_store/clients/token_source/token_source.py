import pprint
from datetime import datetime
from typing import Optional

from h2o_secure_store.gen.model.v1_token_source import V1TokenSource


class TokenSource:
    def __init__(
            self,
            name: str,
            redirect_uri: str,
            login_uri: str,
            login_required: bool,
            access_token: str,
            issue_time: Optional[datetime],
            expire_time: datetime,
            subject: str,
            login_principal: str,
            creator: str,
            uid: str,
            create_time: datetime,
            login_time: Optional[datetime],
    ):
        self.name = name
        self.redirect_uri = redirect_uri
        self.login_uri = login_uri
        self.login_required = login_required
        self.access_token = access_token
        self.issue_time = issue_time
        self.expire_time = expire_time
        self.subject = subject
        self.login_principal = login_principal
        self.creator = creator
        self.uid = uid
        self.create_time = create_time
        self.login_time = login_time

        self.oauth_client_id = ""
        self.token_source_id = ""
        if name:
            self.oauth_client_id = self.name.split("/")[1]
            self.token_source_id = self.name.split("/")[3]

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def to_api_object(self) -> V1TokenSource:
        return V1TokenSource(
            name=self.name,
            redirect_uri=self.redirect_uri,
            login_uri=self.login_uri,
            login_required=self.login_required,
            access_token=self.access_token,
            issue_time=self.issue_time,
            expire_time=self.expire_time,
            subject=self.subject,
            login_principal=self.login_principal,
            creator=self.creator,
            uid=self.uid,
            create_time=self.create_time,
            login_time=self.login_time,
        )


def from_api_object(api_object: V1TokenSource) -> TokenSource:
    return TokenSource(
        name=api_object.name,
        redirect_uri=api_object.redirect_uri,
        login_uri=api_object.login_uri,
        login_required=api_object.login_required,
        access_token=api_object.access_token,
        issue_time=api_object.issue_time,
        expire_time=api_object.expire_time,
        subject=api_object.subject,
        login_principal=api_object.login_principal,
        creator=api_object.creator,
        uid=api_object.uid,
        create_time=api_object.create_time,
        login_time=api_object.login_time,
    )
