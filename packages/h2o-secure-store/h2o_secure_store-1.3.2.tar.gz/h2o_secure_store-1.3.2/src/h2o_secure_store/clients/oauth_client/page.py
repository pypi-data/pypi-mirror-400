import pprint

from h2o_secure_store.clients.oauth_client.oauth_client import from_api_object
from h2o_secure_store.gen.model.v1_list_o_auth_clients_response import (
    V1ListOAuthClientsResponse,
)


class OAuthClientsPage:
    """Class represents a list of OAuthClients together with a next_page_token for listing all OAuthClients."""

    def __init__(self, list_api_response: V1ListOAuthClientsResponse) -> None:
        api_objects = list_api_response.oauth_clients
        self.oauth_clients = []
        for api_oauth_client in api_objects:
            self.oauth_clients.append(from_api_object(api_oauth_client))

        self.next_page_token = list_api_response.next_page_token

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)
