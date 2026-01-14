from typing import Dict
from typing import List
from typing import Optional

from h2o_secure_store.clients.auth.token_api_client import TokenApiClient
from h2o_secure_store.clients.connection_config import ConnectionConfig
from h2o_secure_store.clients.secret.page import SecretsPage
from h2o_secure_store.clients.secret.secret import Secret
from h2o_secure_store.clients.secret.secret import from_api_object
from h2o_secure_store.exception import CustomApiException
from h2o_secure_store.gen import ApiException
from h2o_secure_store.gen import Configuration
from h2o_secure_store.gen.api.secret_service_api import SecretServiceApi
from h2o_secure_store.gen.model.v1_list_secrets_response import V1ListSecretsResponse
from h2o_secure_store.gen.model.v1_secret import V1Secret


class SecretClient:
    """SecretClient manages Secrets."""

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
            self.api_instance = SecretServiceApi(api_client)

    def create_secret(
            self,
            parent: str,
            secret_id: str = "",
            display_name: str = "",
            annotations: Dict[str, str] = None,
    ) -> Secret:
        """Creates a Secret.

        Args:
            parent (str): The resource name of the workspace to associate with the Secret.
                Format is `workspaces/*`.
            secret_id (str, optional): The ID to use for the Secret, which will become the final component
                of the secret's resource name.
                If left unspecified, the server will generate one.
                This value must:
                - contain 1-63 characters
                - contain only lowercase alphanumeric characters or hyphen ('-')
                - start with an alphabetic character
                - end with an alphanumeric character
            display_name (str, optional): Human-readable name of the Secret. Does not have to be unique.
            annotations (Dict[str, str], optional): Additional arbitrary metadata associated with the Secret. Annotations are key/value pairs.

        Returns:
            Secret: Secret object.
        """
        created_api_object: V1Secret

        try:
            created_api_object = self.api_instance.secret_service_create_secret(
                parent=parent,
                secret=Secret(
                    display_name=display_name,
                    annotations=annotations if annotations is not None else {},
                ).to_api_object(),
                secret_id=secret_id,
            ).secret
        except ApiException as e:
            raise CustomApiException(e)
        return from_api_object(api_object=created_api_object)

    def get_secret(self, name: str) -> Secret:
        """Returns a Secret.

        Args:
            name (str): The resource name of the Secret. Format is `workspaces/*/secrets/*`.

        Returns:
            Secret: Secret object.
        """
        api_object: V1Secret

        try:
            api_object = self.api_instance.secret_service_get_secret(
                name_1=name
            ).secret
        except ApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=api_object)

    def list_secrets(
            self,
            parent: str,
            page_size: int = 0,
            page_token: str = "",
            show_deleted: bool = False,
    ) -> SecretsPage:
        """Lists Secrets.

        Args:
            parent (str): The resource name of the workspace from which to list Secrets.
                Format is `workspaces/*`.
            page_size (int): Maximum number of Secrets to return in a response.
                If unspecified (or set to 0), at most 50 Secrets will be returned.
                The maximum value is 1000; values above 1000 will be coerced to 1000.
            page_token (str): Page token.
                Leave unset to receive the initial page.
                To list any subsequent pages use the value of 'next_page_token' returned from the SecretsPage.
            show_deleted (bool): If set to true, include deleted Secrets in the response.

        Returns:
            SecretsPage: SecretsPage object.
        """
        list_response: V1ListSecretsResponse

        try:
            list_response = (
                self.api_instance.secret_service_list_secrets(
                    parent=parent,
                    page_size=page_size,
                    page_token=page_token,
                    show_deleted=show_deleted,
                )
            )
        except ApiException as e:
            raise CustomApiException(e)

        return SecretsPage(list_response)

    def list_all_secrets(self, parent: str, show_deleted: bool = False) -> List[Secret]:
        """ List all Secrets.

        Args:
            parent (str): The resource name of the workspace from which to list Secrets.
                Format is `workspaces/*`.
            show_deleted (bool): If set to true, include deleted Secrets in the response.

        Returns:
            List of Secret.
        """
        all_secrets: List[Secret] = []
        next_page_token = ""
        while True:
            secret_list = self.list_secrets(
                parent=parent,
                page_size=0,
                page_token=next_page_token,
                show_deleted=show_deleted,
            )
            all_secrets = all_secrets + secret_list.secrets
            next_page_token = secret_list.next_page_token
            if next_page_token == "":
                break

        return all_secrets

    def delete_secret(self, name: str) -> Secret:
        """Deletes a Secret and the child SecretVersions.
        A deleted secret is purged after 30 days but can be restored using the undelete method.

        Args:
            name (str): The resource name of the Secret. Format is `workspaces/*/secrets/*`.
        """
        api_object: V1Secret

        try:
            api_object = self.api_instance.secret_service_delete_secret(
                name_1=name
            ).secret
        except ApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=api_object)

    def undelete_secret(self, name: str) -> Secret:
        """Undeletes a deleted Secret and the child SecretVersions.

        Args:
            name (str): The resource name of the Secret. Format is `workspaces/*/secrets/*`.
        """
        api_object: V1Secret

        try:
            api_object = self.api_instance.secret_service_undelete_secret(
                name=name,
                body={},
            ).secret
        except ApiException as e:
            raise CustomApiException(e)

        return from_api_object(api_object=api_object)

    def delete_all_secrets(self, parent: str) -> None:
        """Delete all Secrets."""
        for n in self.list_all_secrets(parent=parent, show_deleted=False):
            self.delete_secret(name=n.name)

