import http

import pytest

from h2o_secure_store.clients.base.workspace import DEFAULT_WORKSPACE
from h2o_secure_store.clients.secret.client import SecretClient
from h2o_secure_store.clients.secret.state import SecretState
from h2o_secure_store.exception import CustomApiException


def test_delete_secret(
        delete_secret_rows_before,
        user_secret_client: SecretClient,
):
    s = user_secret_client.create_secret(
        parent=DEFAULT_WORKSPACE,
        secret_id="secret1",
    )

    deleted = user_secret_client.delete_secret(name=s.name)

    assert deleted.name == f"workspaces/{s.get_workspace_id()}/secrets/secret1"
    assert deleted.state == SecretState.STATE_DELETED
    assert deleted.creator != ""
    assert deleted.create_time is not None
    assert deleted.delete_time is not None
    assert deleted.purge_time is not None
    assert deleted.deleter == deleted.creator

    assert deleted.delete_time > deleted.create_time
    assert deleted.purge_time > deleted.delete_time


def test_delete_deleted_secret(
        delete_secret_rows_before,
        user_secret_client: SecretClient,
):
    s = user_secret_client.create_secret(
        parent=DEFAULT_WORKSPACE,
        secret_id="secret1",
    )

    user_secret_client.delete_secret(name=s.name)

    with pytest.raises(CustomApiException) as exc:
        user_secret_client.delete_secret(name=s.name)
    assert exc.value.status == http.HTTPStatus.NOT_FOUND


def test_delete_secret_not_found(
        user_secret_client: SecretClient,
):
    with pytest.raises(CustomApiException) as exc:
        user_secret_client.delete_secret(name=f"{DEFAULT_WORKSPACE}/secrets/non-existing")
    assert exc.value.status == http.HTTPStatus.NOT_FOUND
