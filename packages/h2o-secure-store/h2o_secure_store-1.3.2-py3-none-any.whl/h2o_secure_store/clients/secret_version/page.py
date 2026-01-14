import pprint

from h2o_secure_store.clients.secret_version.secret_version import from_api_object
from h2o_secure_store.gen.model.v1_list_secret_versions_response import (
    V1ListSecretVersionsResponse,
)


class SecretVersionsPage:
    """Class represents a list of SecretVersions together with a next_page_token for listing all SecretVersions."""

    def __init__(self, list_api_response: V1ListSecretVersionsResponse) -> None:
        api_objects = list_api_response.secret_versions
        self.secret_versions = []
        for api_secret_version in api_objects:
            self.secret_versions.append(from_api_object(api_secret_version))

        self.next_page_token = list_api_response.next_page_token

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)
