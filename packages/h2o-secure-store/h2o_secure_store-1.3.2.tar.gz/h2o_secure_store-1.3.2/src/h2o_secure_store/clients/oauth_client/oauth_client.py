import pprint
from datetime import datetime
from typing import List
from typing import Optional

from h2o_secure_store.gen.model.o_auth_client_resource import OAuthClientResource
from h2o_secure_store.gen.model.v1_o_auth_client import V1OAuthClient


class OAuthClient:
    def __init__(
        self,
        issuer: str,
        client_id: str,
        name: str,
        display_name: str,
        client_secret: str,
        client_secret_set: bool,
        authorization_endpoint: str,
        token_endpoint: str,
        extra_scopes: List[str],
        refresh_disabled: bool,
        login_principal_claim: str,
        callback_uri: str,
        creator: str,
        updater: str,
        uid: str,
        create_time: datetime,
        update_time: Optional[datetime] = None,
    ):
        self.issuer = issuer
        self.client_id = client_id
        self.name = name
        self.display_name = display_name
        self.client_secret = client_secret
        self.client_secret_set = client_secret_set
        self.authorization_endpoint = authorization_endpoint
        self.token_endpoint = token_endpoint
        self.extra_scopes = extra_scopes
        self.refresh_disabled = refresh_disabled
        self.login_principal_claim = login_principal_claim
        self.callback_uri = callback_uri
        self.creator = creator
        self.updater = updater
        self.uid = uid
        self.create_time = create_time
        self.update_time = update_time

        self.oauth_client_id = ""
        if name:
            self.oauth_client_id = self.name.split("/")[1]

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def to_api_object(self) -> V1OAuthClient:
        return V1OAuthClient(
            issuer=self.issuer,
            client_id=self.client_id,
            name=self.name,
            display_name=self.display_name,
            client_secret=self.client_secret,
            client_secret_set=self.client_secret_set,
            authorization_endpoint=self.authorization_endpoint,
            token_endpoint=self.token_endpoint,
            extra_scopes=self.extra_scopes,
            refresh_disabled=self.refresh_disabled,
            login_principal_claim=self.login_principal_claim,
            callback_uri=self.callback_uri,
            creator=self.creator,
            updater=self.updater,
            uid=self.uid,
            create_time=self.create_time,
            update_time=self.update_time,
        )

    def to_resource(self) -> OAuthClientResource:
        # This class (OAuthClientResource) is required by Update method.
        # Need to create this instance via protected method _from_openapi_data due to the generated code.
        return OAuthClientResource._from_openapi_data(
            issuer=self.issuer,
            client_id=self.client_id,
            display_name=self.display_name,
            client_secret=self.client_secret,
            client_secret_set=self.client_secret_set,
            authorization_endpoint=self.authorization_endpoint,
            token_endpoint=self.token_endpoint,
            extra_scopes=self.extra_scopes,
            refresh_disabled=self.refresh_disabled,
            login_principal_claim=self.login_principal_claim,
            callback_uri=self.callback_uri,
            creator=self.creator,
            updater=self.updater,
            uid=self.uid,
            create_time=self.create_time,
            update_time=self.update_time,
        )


def from_api_object(api_object: V1OAuthClient) -> OAuthClient:
    return OAuthClient(
        issuer=api_object.issuer,
        client_id=api_object.client_id,
        name=api_object.name,
        display_name=api_object.display_name,
        client_secret=api_object.client_secret,
        client_secret_set=api_object.client_secret_set,
        authorization_endpoint=api_object.authorization_endpoint,
        token_endpoint=api_object.token_endpoint,
        extra_scopes=api_object.extra_scopes,
        refresh_disabled=api_object.refresh_disabled,
        login_principal_claim=api_object.login_principal_claim,
        callback_uri=api_object.callback_uri,
        creator=api_object.creator,
        updater=api_object.updater,
        uid=api_object.uid,
        create_time=api_object.create_time,
        update_time=api_object.update_time,
    )
