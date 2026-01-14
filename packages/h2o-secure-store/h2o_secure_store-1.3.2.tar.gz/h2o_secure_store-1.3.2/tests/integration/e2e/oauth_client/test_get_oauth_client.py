import http

import pytest

from h2o_secure_store.exception import CustomApiException


def test_get_oauth_client(
    delete_all_oauth_clients_before_after,
    user_oauth_client_client,
    oauth_client1,
):
    got_oauth_client = user_oauth_client_client.get_oauth_client(oauth_client_id="oauth-client1")

    assert oauth_client1.issuer == got_oauth_client.issuer
    assert oauth_client1.client_id == got_oauth_client.client_id
    assert oauth_client1.name == got_oauth_client.name
    assert oauth_client1.display_name == got_oauth_client.display_name
    assert oauth_client1.client_secret == got_oauth_client.client_secret
    assert oauth_client1.client_secret_set == got_oauth_client.client_secret_set
    assert oauth_client1.authorization_endpoint == got_oauth_client.authorization_endpoint
    assert oauth_client1.token_endpoint == got_oauth_client.token_endpoint
    assert oauth_client1.extra_scopes == got_oauth_client.extra_scopes
    assert oauth_client1.refresh_disabled == got_oauth_client.refresh_disabled
    assert oauth_client1.login_principal_claim == got_oauth_client.login_principal_claim
    assert oauth_client1.callback_uri == got_oauth_client.callback_uri
    assert oauth_client1.creator == got_oauth_client.creator
    assert oauth_client1.updater == got_oauth_client.updater
    assert oauth_client1.create_time == got_oauth_client.create_time
    assert oauth_client1.update_time == got_oauth_client.update_time
    assert oauth_client1.uid == got_oauth_client.uid


def test_get_oauth_client_not_found(
    delete_all_oauth_clients_before_after,
    user_oauth_client_client,
):
    with pytest.raises(CustomApiException) as exc:
        user_oauth_client_client.get_oauth_client(
            oauth_client_id="non-existing"
        )

    assert exc.value.status == http.HTTPStatus.NOT_FOUND
