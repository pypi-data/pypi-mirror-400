import pprint

from h2o_secure_store.clients.token_source.token_source import from_api_object
from h2o_secure_store.gen.model.v1_list_token_sources_response import (
    V1ListTokenSourcesResponse,
)


class TokenSourcesPage:
    """Class represents a list of TokenSources together with a next_page_token for listing all TokenSources."""

    def __init__(self, list_api_response: V1ListTokenSourcesResponse) -> None:
        api_objects = list_api_response.token_sources
        self.token_sources = []
        for api_token_source in api_objects:
            self.token_sources.append(from_api_object(api_token_source))

        self.next_page_token = list_api_response.next_page_token

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)
