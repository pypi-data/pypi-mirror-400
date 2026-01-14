from h2o_secure_store.clients.oauth_client.client import OAuthClientClient
from h2o_secure_store.clients.token_source.token_source import TokenSource


def test_invalidate_token_sources(
        delete_all_token_sources_before_after,
        token_source1: TokenSource,
        user_oauth_client_client: OAuthClientClient,
):
    # Cannot test invalidating token sources, only verify that it doesn't throw an error
    user_oauth_client_client.invalidate_token_sources(token_source1.oauth_client_id)
