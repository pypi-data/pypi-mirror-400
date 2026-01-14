import http

import pytest

from h2o_secure_store.clients.oauth_client.oauth_client import OAuthClient
from h2o_secure_store.clients.token_source.client import TokenSourceClient
from h2o_secure_store.exception import CustomApiException


def test_delete_token_source(
    delete_all_token_sources_before_after,
    oauth_client1: OAuthClient,
    user_token_source_client: TokenSourceClient,
):
    token_source = user_token_source_client.create_token_source(
        oauth_client_id=oauth_client1.oauth_client_id,
        redirect_uri="http://localhost:8080",
        token_source_id="token-source-delete",
    )

    user_token_source_client.delete_token_source(
        token_source_id=token_source.token_source_id, oauth_client_id=oauth_client1.oauth_client_id
    )

    with pytest.raises(CustomApiException) as exc:
        user_token_source_client.delete_token_source(
            token_source_id="oauth-client1", oauth_client_id=oauth_client1.oauth_client_id
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND


def test_delete_token_source_not_found(
    delete_all_token_sources_before_after,
    oauth_client1: OAuthClient,
    user_token_source_client: TokenSourceClient,
):
    with pytest.raises(CustomApiException) as exc:
        user_token_source_client.delete_token_source(
            token_source_id="non-existing", oauth_client_id=oauth_client1.oauth_client_id
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND


def test_delete_token_source_forbidden(
        delete_all_token_sources_before_after,
        token_source1,
        user_2_token_source_client: TokenSourceClient,
):
    with pytest.raises(CustomApiException) as exc:
        # token_source1 is created with user_token_source_client - different user
        user_2_token_source_client.delete_token_source(
            token_source_id=token_source1.token_source_id, oauth_client_id=token_source1.oauth_client_id
        )
    assert exc.value.status == http.HTTPStatus.FORBIDDEN
