import http

import pytest

from h2o_secure_store.clients.base.workspace import DEFAULT_WORKSPACE
from h2o_secure_store.clients.secret.client import SecretClient
from h2o_secure_store.clients.secret.state import SecretState
from h2o_secure_store.exception import CustomApiException


def test_get_secret(
        delete_secret_rows_before,
        user_secret_client: SecretClient,
):
    user_secret_client.create_secret(
        parent=DEFAULT_WORKSPACE,
        secret_id="secret1",
    )

    secret = user_secret_client.get_secret(name=f"{DEFAULT_WORKSPACE}/secrets/secret1")

    assert secret.name == f"workspaces/{secret.get_workspace_id()}/secrets/secret1"
    assert secret.state == SecretState.STATE_ACTIVE
    assert secret.creator != ""
    assert secret.create_time is not None
    assert secret.delete_time is None
    assert secret.purge_time is None
    assert secret.deleter == ""
    assert secret.uid != ""


def test_get_secret_not_found(
        user_secret_client: SecretClient,
):
    with pytest.raises(CustomApiException) as exc:
        user_secret_client.get_secret(name=f"{DEFAULT_WORKSPACE}/secrets/non-existing")
    assert exc.value.status == http.HTTPStatus.NOT_FOUND
