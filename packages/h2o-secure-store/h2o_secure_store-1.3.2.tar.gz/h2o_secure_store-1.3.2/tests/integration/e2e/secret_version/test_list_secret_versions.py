import http

import pytest

''
from h2o_secure_store.clients.secret.client import SecretClient
from h2o_secure_store.clients.secret_version.client import SecretVersionClient
from h2o_secure_store.clients.secret_version.secret_version import SecretVersion
from h2o_secure_store.exception import CustomApiException


@pytest.mark.parametrize(
    ["page_size", "page_token"],
    [
        (-20, ""),
        (0, "non-existing-token"),
    ],
)
def test_list_validation(user_allowed_secret_version_client, secret_user_allowed, page_size, page_token):
    with pytest.raises(CustomApiException) as exc:
        user_allowed_secret_version_client.list_secret_versions(
            parent=secret_user_allowed.name,
            page_size=page_size,
            page_token=page_token,
        )
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST


def test_list_secret_versions_pagination(
        delete_secret_rows_before,
        secret_user_allowed,
        user_allowed_secret_version_client: SecretVersionClient,
):
    assert_list_secret_versions_pagination(
        secret_name=secret_user_allowed.name,
        secret_version_client_tested=user_allowed_secret_version_client,
    )


def test_list_all_secret_versions(delete_secret_rows_before,
                                  secret_user_allowed,
                                  user_allowed_secret_version_client: SecretVersionClient):
    # Arrange
    create_testing_secrets(
        secret_name=secret_user_allowed.name,
        secret_version_client_creator=user_allowed_secret_version_client,
    )

    # Test basic list_all.
    secrets = user_allowed_secret_version_client.list_all_secret_versions(
        parent=secret_user_allowed.name,
    )
    assert len(secrets) == 3


def test_list_secret_versions_deleted_secret(delete_secret_rows_before,
                                             secret_user_allowed,
                                             user_secret_client: SecretClient,
                                             user_allowed_secret_version_client: SecretVersionClient):
    create_testing_secrets(
        secret_name=secret_user_allowed.name,
        secret_version_client_creator=user_allowed_secret_version_client,
    )
    user_secret_client.delete_secret(name=secret_user_allowed.name)

    with pytest.raises(CustomApiException) as exc:
        user_allowed_secret_version_client.list_secret_versions(parent=secret_user_allowed.name, page_size=100, show_deleted=False)
    assert exc.value.status == http.HTTPStatus.NOT_FOUND


def assert_list_secret_versions_pagination(
        secret_name: str,
        secret_version_client_tested: SecretVersionClient,
):
    # Test no secrets found.
    page = secret_version_client_tested.list_secret_versions(parent=secret_name)
    assert len(page.secret_versions) == 0
    assert page.next_page_token == ""

    # Arrange
    create_testing_secrets(secret_name, secret_version_client_tested)

    # Test getting first page.
    page = secret_version_client_tested.list_secret_versions(
        parent=secret_name,
        page_size=1,
    )
    assert len(page.secret_versions) == 1
    assert page.next_page_token != ""

    # Test getting second page.
    page = secret_version_client_tested.list_secret_versions(
        parent=secret_name,
        page_size=1,
        page_token=page.next_page_token,
    )
    assert len(page.secret_versions) == 1
    assert page.next_page_token != ""

    # Test getting last page.
    page = secret_version_client_tested.list_secret_versions(
        parent=secret_name,
        page_size=1,
        page_token=page.next_page_token,
    )
    assert len(page.secret_versions) == 1
    assert page.next_page_token == ""

    # Test exceeding max page size.
    page = secret_version_client_tested.list_secret_versions(
        parent=secret_name,
        page_size=1001,
    )
    assert len(page.secret_versions) == 3
    assert page.next_page_token == ""


def create_testing_secrets(secret_name: str, secret_version_client_creator: SecretVersionClient):
    secret_version_client_creator.create_secret_version(
        parent=secret_name,
        secret_version=SecretVersion(
            value=b"secret_value1"
        ),
    )
    secret_version_client_creator.create_secret_version(
        parent=secret_name,
        secret_version=SecretVersion(
            value=b"secret_value2"
        ),
    )
    secret_version_client_creator.create_secret_version(
        parent=secret_name,
        secret_version=SecretVersion(
            value=b"secret_value3"
        ),
    )
