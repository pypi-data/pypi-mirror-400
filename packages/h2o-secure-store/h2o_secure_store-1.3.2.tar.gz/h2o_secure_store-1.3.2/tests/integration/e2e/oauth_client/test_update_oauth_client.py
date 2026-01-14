import http
import json

import pytest

from h2o_secure_store.exception import CustomApiException


def test_update_oauth_client(
    delete_all_oauth_clients_before_after,
    user_oauth_client_client,
    oauth_client1,
):
    assert oauth_client1.client_id == "client1"
    assert oauth_client1.display_name == ""
    assert oauth_client1.extra_scopes == []
    assert oauth_client1.refresh_disabled is False
    assert oauth_client1.login_principal_claim == "preferred_username"

    oauth_client1.client_id = "new-client1"
    oauth_client1.display_name = "new display name"
    oauth_client1.extra_scopes = ["alpha", "beta"]
    oauth_client1.refresh_disabled = True
    oauth_client1.login_principal_claim = "new-login-principal-claim"

    # Update all update-able fields.
    updated = user_oauth_client_client.update_oauth_client(
        oauth_client=oauth_client1,
    )

    assert updated.client_id == "client1"
    assert updated.display_name == "new display name"
    assert updated.extra_scopes == ["alpha", "beta"]
    assert updated.refresh_disabled is True
    assert updated.login_principal_claim == "new-login-principal-claim"

    # Update specified fields.
    updated.client_id = "new-client2"
    updated.display_name = "new display name 2"
    updated.extra_scopes = ["alpha2", "beta2"]
    updated.refresh_disabled = False
    updated.login_principal_claim = "new-login-principal-claim2"
    updated_again = user_oauth_client_client.update_oauth_client(
        oauth_client=updated,
        update_mask="display_name,login_principal_claim",
    )

    assert updated_again.client_id == "client1"
    assert updated_again.display_name == "new display name 2"
    assert updated_again.extra_scopes == ["alpha", "beta"]
    assert updated_again.refresh_disabled is True
    assert updated_again.login_principal_claim == "new-login-principal-claim2"


def test_update_oauth_client_not_found(
    delete_all_oauth_clients_before_after,
    user_oauth_client_client,
    oauth_client1,
):
    oauth_client1.oauth_client_id = "whatever"
    oauth_client1.name = "oauthClients/whatever"
    with pytest.raises(CustomApiException) as exc:
        user_oauth_client_client.update_oauth_client(
            oauth_client=oauth_client1
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND


def test_update_oauth_client_validation(
    delete_all_oauth_clients_before_after,
    user_oauth_client_client,
    oauth_client1,
):
    assert oauth_client1.extra_scopes == []
    oauth_client1.extra_scopes = [" email"]

    with pytest.raises(CustomApiException) as exc:
        user_oauth_client_client.update_oauth_client(
            oauth_client=oauth_client1,
        )
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST
    assert 'extraScope " email" contains whitespace' in json.loads(exc.value.body)["message"]