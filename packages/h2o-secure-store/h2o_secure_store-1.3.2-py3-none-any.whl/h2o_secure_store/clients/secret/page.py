import pprint

from h2o_secure_store.clients.secret.secret import from_api_object
from h2o_secure_store.gen.model.v1_list_secrets_response import V1ListSecretsResponse


class SecretsPage:
    """Class represents a list of Secrets together with a next_page_token for listing all Secrets."""

    def __init__(self, list_api_response: V1ListSecretsResponse) -> None:
        api_objects = list_api_response.secrets
        self.secrets = []
        for api_secret in api_objects:
            self.secrets.append(from_api_object(api_secret))

        self.next_page_token = list_api_response.next_page_token

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)
