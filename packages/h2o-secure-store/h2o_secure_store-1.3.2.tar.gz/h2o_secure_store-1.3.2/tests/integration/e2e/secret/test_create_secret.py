import http

import pytest

from h2o_secure_store.clients.base.workspace import DEFAULT_WORKSPACE
from h2o_secure_store.clients.secret.client import SecretClient
from h2o_secure_store.clients.secret.state import SecretState
from h2o_secure_store.exception import CustomApiException


def test_create_secret(
        delete_secret_rows_before,
        user_secret_client: SecretClient,
):
    secret = user_secret_client.create_secret(
        parent=DEFAULT_WORKSPACE,
        secret_id="secret1",
        display_name="Test Secret",
        annotations={"key1": "value1", "key2": "value2"},
    )

    assert secret.name == f"workspaces/{secret.get_workspace_id()}/secrets/secret1"
    assert secret.display_name == "Test Secret"
    assert secret.annotations == {"key1": "value1", "key2": "value2"}
    assert secret.state == SecretState.STATE_ACTIVE
    assert secret.creator != ""
    assert secret.create_time is not None
    assert secret.delete_time is None
    assert secret.purge_time is None
    assert secret.deleter == ""
    assert secret.uid != ""


def test_create_secret_generate_secret_id(
        delete_secret_rows_before,
        user_secret_client: SecretClient,
):
    s1 = user_secret_client.create_secret(
        parent=DEFAULT_WORKSPACE,
    )

    s2 = user_secret_client.create_secret(
        parent=DEFAULT_WORKSPACE,
    )

    assert s1.name != s2.name
    assert s1.get_secret_id() != s2.get_secret_id()


def test_create_secret_already_exists(
        delete_secret_rows_before,
        user_secret_client: SecretClient,
):
    secret = user_secret_client.create_secret(
        parent=DEFAULT_WORKSPACE,
        secret_id="secret1",
    )

    with pytest.raises(CustomApiException) as exc:
        # Try to create Kernel with the same ID.
        user_secret_client.create_secret(
            parent=DEFAULT_WORKSPACE,
            secret_id=secret.get_secret_id(),
        )

    # grpc AlreadyExists == http Conflict 409
    assert exc.value.status == http.HTTPStatus.CONFLICT


def test_create_secret_workspace_not_found(
        user_secret_client: SecretClient,
):
    with pytest.raises(CustomApiException) as exc:
        user_secret_client.create_secret(
            parent="workspaces/non-existing",
            secret_id="secret1",
        )

    assert exc.value.status == http.HTTPStatus.FORBIDDEN


def test_create_secret_workspace_forbidden(
        delete_secret_rows_before,
        user_secret_client: SecretClient,
        user_2_secret_client: SecretClient,
):
    s1 = user_secret_client.create_secret(
        parent=DEFAULT_WORKSPACE,
    )

    with pytest.raises(CustomApiException) as exc:
        user_2_secret_client.create_secret(
            parent=f"workspaces/{s1.get_workspace_id()}",
            secret_id="secret2",
        )

    assert exc.value.status == http.HTTPStatus.FORBIDDEN

