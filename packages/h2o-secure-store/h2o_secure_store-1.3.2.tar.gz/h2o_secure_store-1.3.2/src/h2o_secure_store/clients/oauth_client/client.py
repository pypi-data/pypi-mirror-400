from typing import List
from typing import Optional

from h2o_secure_store.clients.auth.token_api_client import TokenApiClient
from h2o_secure_store.clients.connection_config import ConnectionConfig
from h2o_secure_store.clients.oauth_client.oauth_client import OAuthClient
from h2o_secure_store.clients.oauth_client.oauth_client import from_api_object
from h2o_secure_store.clients.oauth_client.page import OAuthClientsPage
from h2o_secure_store.exception import CustomApiException
from h2o_secure_store.gen import ApiException
from h2o_secure_store.gen import Configuration
from h2o_secure_store.gen.api.o_auth_client_service_api import OAuthClientServiceApi
from h2o_secure_store.gen.model.v1_list_o_auth_clients_response import (
    V1ListOAuthClientsResponse,
)
from h2o_secure_store.gen.model.v1_o_auth_client import V1OAuthClient


class OAuthClientClient:
    """OAuthClientClient manages OAuthClients."""

    def __init__(
            self,
            connection_config: ConnectionConfig,
            verify_ssl: bool = True,
            ssl_ca_cert: Optional[str] = None,
    ):
        configuration = Configuration(host=connection_config.server_url)
        configuration.verify_ssl = verify_ssl
        configuration.ssl_ca_cert = ssl_ca_cert

        with TokenApiClient(
                configuration, connection_config.token_provider
        ) as api_client:
            self.api_instance = OAuthClientServiceApi(api_client)

    def create_oauth_client(
            self,
            issuer: str,
            client_id: str,
            oauth_client_id: str = "",
            authorization_endpoint: str = "",
            token_endpoint: str = "",
            extra_scopes: List[str] = None,
            refresh_disabled: bool = False,
            login_principal_claim: str = "",
            client_secret: str = "",
            display_name: str = "",
    ) -> OAuthClient:
        """Creates a OAuthClient.

        Args:
            issuer (str): The issuer URL of the OAuthClient.
                It is the URI of the IDP that the OAuth Client is registered with.
                In Okta it is the Authorization Server Issuer URI.
                For example, "https://dev-123456.okta.com/oauth2/ausads85d7".
            client_id (str): The client ID of the OAuthClient.
            oauth_client_id (str, optional): The ID to use for the OAuthClient, which will become the final component of the oauth_client's resource name.
                If left unspecified, the server will generate one.
                This value must:

                - contain 1-63 characters
                - contain only lowercase alphanumeric characters or hyphen ('-')
                - start with an alphabetic character
                - end with an alphanumeric character
            authorization_endpoint (str, optional): The authorization endpoint of the OAuthClient.
                For example, "https://dev-123456.okta.com/oauth2/ausads85d7/v1/authorize".
                If not set, it is discovered from the issuer.
            token_endpoint (str, optional): The token endpoint of the OAuthClient.
                For example, "https://dev-123456.okta.com/oauth2/ausads85d7/v1/token".
                If not set, it is discovered from the issuer.
            extra_scopes (List[str], optional): Extra scopes for the OAuthClient.
                Optional. A list of additional scopes to request from the OAuth Client.
                The "openid" scope is always included and does not need to be specified.
                The "offline_access" scope is included if "refresh_disabled" is not set.
                Please note that:
                The "profile" scope is strongly recommended if "login_principal_claim" is not set to "sub".
                The "email" scope is strongly recommended if "login_principal_claim" is set to "email".
                Recommended to set as ["profile", "email"].
            refresh_disabled (bool, optional): If set to true, the "offline_access" scope is not requested.
                This means that the TokenSource will not be able to refresh tokens.
                When the Token expires, the user will need to log in again.
                Defaults to false.
            login_principal_claim (str, optional): The ID Token claim name for the login principal.
                Once the login is successful, it is extracted into TokenProvider.login_principal field.
                Defaults to "preferred_username".
            client_secret (str, optional): The client secret of the OAuthClient.
            display_name (str, optional): Human-readable name of the OAuthClient. Must contain at most 63 characters. Does not have to be unique.

        Returns:
            OAuthClient: OAuthClient object.
        """
        if extra_scopes is None:
            extra_scopes = []

        api_object = V1OAuthClient(
            display_name=display_name,
            client_secret=client_secret,
            issuer=issuer,
            client_id=client_id,
            authorization_endpoint=authorization_endpoint,
            token_endpoint=token_endpoint,
            extra_scopes=extra_scopes,
            refresh_disabled=refresh_disabled,
            login_principal_claim=login_principal_claim,
        )
        created_api_object: V1OAuthClient

        try:
            created_api_object = self.api_instance.o_auth_client_service_create_o_auth_client(
                oauth_client=api_object, oauth_client_id=oauth_client_id
            ).oauth_client
        except ApiException as e:
            raise CustomApiException(e)
        return from_api_object(api_object=created_api_object)

    def get_oauth_client(self, oauth_client_id: str) -> OAuthClient:
        """Returns a OAuthClient.

        Args:
            oauth_client_id (str): OAuthClient ID.

        Returns:
            OAuthClient: OAuthClient object.
        """
        api_object: V1OAuthClient

        try:
            api_object = self.api_instance.o_auth_client_service_get_o_auth_client(
                name=self.build_resource_name(resource_id=oauth_client_id)
            ).oauth_client
        except ApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=api_object)

    def update_oauth_client(self, oauth_client: OAuthClient, update_mask: str = "*") -> OAuthClient:
        """Updates a OAuthClient.

        Args:
            oauth_client (OAuthClient): OAuthClient object with updated fields.
            update_mask (str, optional): The field mask to use for the update.
                Allowed field paths are: {"display_name", "extra_scopes", "refresh_disabled", "login_principal_claim"}.

                If not set, all fields will be updated.
                Defaults to "*".

        Returns:
            OAuthClient: Updated OAuthClient object.
        """
        updated_api_object: V1OAuthClient

        try:
            updated_api_object = (
                self.api_instance.o_auth_client_service_update_o_auth_client(
                    oauth_client_name=oauth_client.name,
                    update_mask=update_mask,
                    oauth_client=oauth_client.to_resource(),
                ).oauth_client
            )
        except ApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=updated_api_object)

    def invalidate_token_sources(self, oauth_client_id: str) -> None:
        """Invalidates all TokenSources for a OAuthClient.

        Args:
            oauth_client_id (str): OAuthClient ID.
        """
        try:
            self.api_instance.o_auth_client_service_invalidate_token_sources(
                name=self.build_resource_name(resource_id=oauth_client_id),
                body=None,
            )
        except ApiException as e:
            raise CustomApiException(e)

    def list_oauth_clients(
            self,
            page_size: int = 0,
            page_token: str = "",
    ) -> OAuthClientsPage:
        """Lists OAuthClients.

        Args:
            page_size (int): Maximum number of OAuthClients to return in a response.
                If unspecified (or set to 0), at most 50 OAuthClients will be returned.
                The maximum value is 1000; values above 1000 will be coerced to 1000.
            page_token (str): Page token.
                Leave unset to receive the initial page.
                To list any subsequent pages use the value of 'next_page_token' returned from the OAuthClientsPage.

        Returns:
            OAuthClientsPage: OAuthClientsPage object.
        """
        list_response: V1ListOAuthClientsResponse

        try:
            list_response = (
                self.api_instance.o_auth_client_service_list_o_auth_clients(
                    page_size=page_size,
                    page_token=page_token,
                )
            )
        except ApiException as e:
            raise CustomApiException(e)

        return OAuthClientsPage(list_response)

    def list_all_oauth_clients(self) -> List[OAuthClient]:
        """ List all OAuthClients.

        Returns:
            List of OAuthClient.
        """
        all_oauth_clients: List[OAuthClient] = []
        next_page_token = ""
        while True:
            oauth_client_list = self.list_oauth_clients(
                page_size=0,
                page_token=next_page_token,
            )
            all_oauth_clients = all_oauth_clients + oauth_client_list.oauth_clients
            next_page_token = oauth_client_list.next_page_token
            if next_page_token == "":
                break

        return all_oauth_clients

    def delete_oauth_client(self, oauth_client_id: str) -> None:
        """Deletes a OAuthClient.

        Args:
            oauth_client_id (str): OAuthClient ID.
        """
        try:
            self.api_instance.o_auth_client_service_delete_o_auth_client(
                name=self.build_resource_name(resource_id=oauth_client_id)
            )
        except ApiException as e:
            raise CustomApiException(e)

    def delete_all_oauth_clients(self) -> None:
        """Delete all OAuthClients."""
        for n in self.list_all_oauth_clients():
            self.delete_oauth_client(oauth_client_id=n.oauth_client_id)

    @staticmethod
    def build_resource_name(resource_id: str) -> str:
        """Helper function for building resource name."""
        return f"oauthClients/{resource_id}"
