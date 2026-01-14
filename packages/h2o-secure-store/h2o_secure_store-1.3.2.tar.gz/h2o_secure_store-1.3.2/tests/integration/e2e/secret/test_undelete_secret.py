import http

import pytest

from h2o_secure_store.clients.base.workspace import DEFAULT_WORKSPACE
from h2o_secure_store.clients.secret.client import SecretClient
from h2o_secure_store.clients.secret.state import SecretState
from h2o_secure_store.exception import CustomApiException


def test_undelete_secret(
        delete_secret_rows_before,
        user_secret_client: SecretClient,
):
    s = user_secret_client.create_secret(
        parent=DEFAULT_WORKSPACE,
        secret_id="secret1",
    )

    user_secret_client.delete_secret(name=s.name)

    undeleted = user_secret_client.undelete_secret(name=s.name)

    assert undeleted.name == f"workspaces/{s.get_workspace_id()}/secrets/secret1"
    assert undeleted.state == SecretState.STATE_ACTIVE
    assert undeleted.creator != ""
    assert undeleted.create_time is not None
    assert undeleted.delete_time is None
    assert undeleted.purge_time is None
    assert undeleted.deleter == ""


def test_undelete_undeleted_secret(
        delete_secret_rows_before,
        user_secret_client: SecretClient,
):
    s = user_secret_client.create_secret(
        parent=DEFAULT_WORKSPACE,
        secret_id="secret1",
    )

    with pytest.raises(CustomApiException) as exc:
        user_secret_client.undelete_secret(name=s.name)
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST


def test_undelete_secret_not_found(
        user_secret_client: SecretClient,
):
    with pytest.raises(CustomApiException) as exc:
        user_secret_client.undelete_secret(name=f"{DEFAULT_WORKSPACE}/secrets/non-existing")
    assert exc.value.status == http.HTTPStatus.NOT_FOUND
