import base64
from typing import List
from typing import Optional

from h2o_secure_store.clients.auth.token_api_client import TokenApiClient
from h2o_secure_store.clients.connection_config import ConnectionConfig
from h2o_secure_store.clients.secret_version.page import SecretVersionsPage
from h2o_secure_store.clients.secret_version.secret_version import SecretVersion
from h2o_secure_store.clients.secret_version.secret_version import from_api_object
from h2o_secure_store.exception import CustomApiException
from h2o_secure_store.gen import ApiException
from h2o_secure_store.gen import Configuration
from h2o_secure_store.gen.api.secret_version_service_api import SecretVersionServiceApi
from h2o_secure_store.gen.model.v1_list_secret_versions_response import (
    V1ListSecretVersionsResponse,
)
from h2o_secure_store.gen.model.v1_secret_version import V1SecretVersion


class SecretVersionClient:
    """SecretVersionClient manages SecretVersions."""

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
            self.api_instance = SecretVersionServiceApi(api_client)

    def create_secret_version(
            self,
            parent: str,
            secret_version: SecretVersion,
    ) -> SecretVersion:
        """Creates a SecretVersion.

        Args:
            parent (str): The resource name of the secret to associate with the SecretVersion.
                Format is `workspaces/*/secrets/*`.
            secret_version (SecretVersion): SecretVersion object to create.

        Returns:
            SecretVersion: SecretVersion object.
        """
        created_api_object: V1SecretVersion

        try:
            created_api_object = self.api_instance.secret_version_service_create_secret_version(
                parent=parent,
                secret_version=secret_version.to_api_object(),
            ).secret_version
        except ApiException as e:
            raise CustomApiException(e)
        return from_api_object(api_object=created_api_object)

    def get_secret_version(self, name: str) -> SecretVersion:
        """Returns a SecretVersion.

        Args:
            name (str): The resource name of the SecretVersion. Format is `workspaces/*/secrets/*/secret_versions/*`.

        Returns:
            SecretVersion: SecretVersion object.
        """
        api_object: V1SecretVersion

        try:
            api_object = self.api_instance.secret_version_service_get_secret_version(
                name_2=name
            ).secret_version
        except ApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=api_object)

    def list_secret_versions(
            self,
            parent: str,
            page_size: int = 0,
            page_token: str = "",
            show_deleted: bool = False,
    ) -> SecretVersionsPage:
        """Lists SecretVersions.

        Args:
            parent (str): The resource name of the secret from which to list SecretVersions.
                Format is `workspaces/*/secrets/*`.
            page_size (int): Maximum number of SecretVersions to return in a response.
                If unspecified (or set to 0), at most 50 SecretVersions will be returned.
                The maximum value is 1000; values above 1000 will be coerced to 1000.
            page_token (str): Page token.
                Leave unset to receive the initial page.
                To list any subsequent pages use the value of 'next_page_token' returned from the SecretVersionsPage.
            show_deleted (bool): If set to true, include deleted SecretVersions in the response.

        Returns:
            SecretVersionsPage: SecretVersionsPage object.
        """
        list_response: V1ListSecretVersionsResponse

        try:
            list_response = (
                self.api_instance.secret_version_service_list_secret_versions(
                    parent=parent,
                    page_size=page_size,
                    page_token=page_token,
                )
            )
        except ApiException as e:
            raise CustomApiException(e)

        return SecretVersionsPage(list_response)

    def list_all_secret_versions(self, parent: str) -> List[SecretVersion]:
        """ List all SecretVersions.

        Args:
            parent (str): The resource name of the secret from which to list SecretVersions.
                Format is `workspaces/*/secrets/*`.

        Returns:
            List of SecretVersion.
        """
        all_secret_versions: List[SecretVersion] = []
        next_page_token = ""
        while True:
            secret_version_list = self.list_secret_versions(
                parent=parent,
                page_size=0,
                page_token=next_page_token,
            )
            all_secret_versions = all_secret_versions + secret_version_list.secret_versions
            next_page_token = secret_version_list.next_page_token
            if next_page_token == "":
                break

        return all_secret_versions

    def reveal_secret_version_value(self, name: str) -> bytes:
        """Reveals a SecretVersion value.

        Args:
            name (str): The resource name of the SecretVersion. Format is `workspaces/*/secrets/*/secretVersions/*`.
        """
        try:
            value = self.api_instance.secret_version_service_reveal_secret_version_value(
                name=name
            ).value
        except ApiException as e:
            raise CustomApiException(e)

        return base64.b64decode(value)
