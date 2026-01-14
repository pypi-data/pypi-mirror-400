from typing import List
from typing import Optional

from h2o_secure_store.clients.auth.token_api_client import TokenApiClient
from h2o_secure_store.clients.connection_config import ConnectionConfig
from h2o_secure_store.clients.token_source.page import TokenSourcesPage
from h2o_secure_store.clients.token_source.token_source import TokenSource
from h2o_secure_store.clients.token_source.token_source import from_api_object
from h2o_secure_store.exception import CustomApiException
from h2o_secure_store.gen import ApiException
from h2o_secure_store.gen import Configuration
from h2o_secure_store.gen.api.token_source_service_api import TokenSourceServiceApi
from h2o_secure_store.gen.model.v1_list_token_sources_response import (
    V1ListTokenSourcesResponse,
)
from h2o_secure_store.gen.model.v1_token_source import V1TokenSource


class TokenSourceClient:
    """TokenSourceClient manages TokenSources."""

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
            self.api_instance = TokenSourceServiceApi(api_client)

    def create_token_source(
            self,
            oauth_client_id: str,
            redirect_uri: str = "",
            token_source_id: str = "",
    ) -> TokenSource:
        """Creates a TokenSource.

        Args:
            oauth_client_id (str): OAuthClient ID.
            token_source_id (str, optional): The ID to use for the TokenSource, which will become the final component of the token source's resource name.
                If left unspecified, the server will generate a random value.
                This value must:

                - contain 1-63 characters
                - contain only lowercase alphanumeric characters or hyphen ('-')
                - start with an alphabetic character
                - end with an alphanumeric character
            redirect_uri (str, optional): The URI to redirect to after the user has successfully logged in.

        Returns:
            TokenSource: TokenSource object.
        """
        api_object = V1TokenSource(
            redirect_uri=redirect_uri,
        )
        created_api_object: V1TokenSource

        try:
            created_api_object = self.api_instance.token_source_service_create_token_source(
                parent=f"oauthClients/{oauth_client_id}", token_source=api_object, token_source_id=token_source_id
            ).token_source
        except ApiException as e:
            raise CustomApiException(e)
        return from_api_object(api_object=created_api_object)

    def get_token_source(self, oauth_client_id: str, token_source_id: str) -> TokenSource:
        """Returns a TokenSource.

        Args:
            oauth_client_id (str): OAuthClient ID.
            token_source_id (str): TokenSource ID.

        Returns:
            TokenSource: TokenSource object.
        """
        api_object: V1TokenSource

        try:
            api_object = self.api_instance.token_source_service_get_token_source(
                name_3=self.build_resource_name(oauth_client_id=oauth_client_id, token_source_id=token_source_id)
            ).token_source
        except ApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=api_object)

    def list_token_sources(
            self,
            oauth_client_id: str,
            page_size: int = 0,
            page_token: str = "",
    ) -> TokenSourcesPage:
        """Lists TokenSources.

        Args:
            oauth_client_id (str): OAuthClient ID.
            page_size (int): Maximum number of TokenSources to return in a response.
                If unspecified (or set to 0), at most 50 TokenSources will be returned.
                The maximum value is 1000; values above 1000 will be coerced to 1000.
            page_token (str): Page token.
                Leave unset to receive the initial page.
                To list any subsequent pages use the value of 'next_page_token' returned from the TokenSourcesPage.

        Returns:
            TokenSourcesPage: TokenSourcesPage object.
        """
        list_response: V1ListTokenSourcesResponse

        try:
            list_response = (
                self.api_instance.token_source_service_list_token_sources(
                    parent=f"oauthClients/{oauth_client_id}",
                    page_size=page_size,
                    page_token=page_token,
                )
            )
        except ApiException as e:
            raise CustomApiException(e)

        return TokenSourcesPage(list_response)

    def list_all_token_sources(self, oauth_client_id: str) -> List[TokenSource]:
        """ Lists all TokenSources.

        Returns:
            List of TokenSource.
        """
        all_token_sources: List[TokenSource] = []
        next_page_token = ""
        while True:
            token_source_list = self.list_token_sources(
                oauth_client_id=oauth_client_id,
                page_size=0,
                page_token=next_page_token,
            )
            all_token_sources = all_token_sources + token_source_list.token_sources
            next_page_token = token_source_list.next_page_token
            if next_page_token == "":
                break

        return all_token_sources

    def delete_token_source(self, oauth_client_id: str, token_source_id: str) -> None:
        """Deletes a TokenSource.

        Args:
            oauth_client_id (str): OAuthClient ID.
            token_source_id (str): TokenSource ID.
        """
        try:
            self.api_instance.token_source_service_delete_token_source(
                name_2=self.build_resource_name(oauth_client_id=oauth_client_id, token_source_id=token_source_id)
            )
        except ApiException as e:
            raise CustomApiException(e)

    def delete_all_token_sources(self, oauth_client_id: str) -> None:
        """Delete all TokenSources."""
        for t in self.list_all_token_sources(oauth_client_id=oauth_client_id):
            self.delete_token_source(oauth_client_id=t.oauth_client_id, token_source_id=t.token_source_id)

    @staticmethod
    def build_resource_name(oauth_client_id: str, token_source_id: str) -> str:
        """Helper function for building resource name."""
        return f"oauthClients/{oauth_client_id}/tokenSources/{token_source_id}"
