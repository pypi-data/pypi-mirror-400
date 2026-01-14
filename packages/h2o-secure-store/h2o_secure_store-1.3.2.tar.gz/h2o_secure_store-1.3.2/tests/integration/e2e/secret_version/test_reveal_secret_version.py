import http

import pytest

from h2o_secure_store.clients.base.workspace import DEFAULT_WORKSPACE
from h2o_secure_store.clients.secret_version.client import SecretVersionClient
from h2o_secure_store.clients.secret_version.secret_version import SecretVersion
from h2o_secure_store.exception import CustomApiException


def test_reveal_secret_version(
        delete_secret_rows_before,
        secret_user_allowed,
        user_allowed_secret_version_client: SecretVersionClient,
):
    secret_version = user_allowed_secret_version_client.create_secret_version(
        parent=secret_user_allowed.name,
        secret_version=SecretVersion(
            value=b"secret_value"
        ),
    )

    secret_version_value = user_allowed_secret_version_client.reveal_secret_version_value(
        name=f"{DEFAULT_WORKSPACE}/secrets/{secret_user_allowed.get_secret_id()}/versions/{secret_version.get_secret_version_id()}"
    )

    assert secret_version_value == b"secret_value"


def test_reveal_latest_secret_version(
        delete_secret_rows_before,
        secret_user_allowed,
        user_allowed_secret_version_client: SecretVersionClient,
):
    latest_secret_value = b"secret_value_latest"

    user_allowed_secret_version_client.create_secret_version(
        parent=secret_user_allowed.name,
        secret_version=SecretVersion(
            value=b"secret_value"
        ),
    )

    user_allowed_secret_version_client.create_secret_version(
        parent=secret_user_allowed.name,
        secret_version=SecretVersion(
            value=latest_secret_value
        ),
    )

    secret_version_value = user_allowed_secret_version_client.reveal_secret_version_value(
        name=f"{DEFAULT_WORKSPACE}/secrets/{secret_user_allowed.get_secret_id()}/versions/latest"
    )

    assert secret_version_value == latest_secret_value


def test_reveal_secret_version_not_found(
        delete_secret_rows_before,
        secret_user_allowed,
        user_allowed_secret_version_client: SecretVersionClient,
):
    with pytest.raises(CustomApiException) as exc:
        user_allowed_secret_version_client.reveal_secret_version_value(
            name=f"{DEFAULT_WORKSPACE}/secrets/{secret_user_allowed.get_secret_id()}/versions/non-existent"
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND


def test_reveal_latest_secret_version_not_found(
        delete_secret_rows_before,
        secret_user_allowed,
        user_allowed_secret_version_client: SecretVersionClient,
):
    with pytest.raises(CustomApiException) as exc:
        user_allowed_secret_version_client.reveal_secret_version_value(
            name=f"{DEFAULT_WORKSPACE}/secrets/{secret_user_allowed.get_secret_id()}/versions/latest"
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND


def test_reveal_secret_version_not_found_parent(
        delete_secret_rows_before,
        user_allowed_secret_version_client: SecretVersionClient,
):
    with pytest.raises(CustomApiException) as exc:
        user_allowed_secret_version_client.reveal_secret_version_value(
            name=f"{DEFAULT_WORKSPACE}/secrets/non-existent/versions/non-existent"
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND
