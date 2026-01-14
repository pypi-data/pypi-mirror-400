import http

import pytest

from h2o_secure_store.clients.base.workspace import DEFAULT_WORKSPACE
from h2o_secure_store.clients.secret.client import SecretClient
from h2o_secure_store.exception import CustomApiException


@pytest.mark.parametrize(
    ["page_size", "page_token"],
    [
        (-20, ""),
        (0, "non-existing-token"),
    ],
)
def test_list_validation(user_secret_client, page_size, page_token):
    with pytest.raises(CustomApiException) as exc:
        user_secret_client.list_secrets(
            parent=DEFAULT_WORKSPACE,
            page_size=page_size,
            page_token=page_token,
        )
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST


def test_list_secrets_pagination(
        delete_secret_rows_before,
        user_secret_client: SecretClient,
):
    assert_list_secrets_pagination(
        secret_client_tested=user_secret_client,
    )


def test_list_all_secrets(delete_secret_rows_before,
                          user_secret_client: SecretClient):
    # Arrange
    create_testing_secrets(secret_client_creator=user_secret_client)

    # Test basic list_all.
    secrets = user_secret_client.list_all_secrets(
        parent=DEFAULT_WORKSPACE,
    )
    assert len(secrets) == 3


def test_list_all_secrets_workspace_separation(delete_secret_rows_before,
                                               user_secret_client: SecretClient,
                                               user_2_secret_client: SecretClient):
    # Arrange
    create_testing_secrets(secret_client_creator=user_secret_client)

    # Test basic list_all as a different user.
    secrets = user_2_secret_client.list_all_secrets(
        parent=DEFAULT_WORKSPACE,
    )
    assert len(secrets) == 0


def test_list_secrets_show_deleted(delete_secret_rows_before,
                                   user_secret_client: SecretClient):
    create_testing_secrets(secret_client_creator=user_secret_client)
    create_testing_secrets_deleted(secret_client_creator=user_secret_client)

    secrets = user_secret_client.list_secrets(parent=DEFAULT_WORKSPACE, page_size=100, show_deleted=False)
    assert len(secrets.secrets) == 3

    secrets = user_secret_client.list_secrets(parent=DEFAULT_WORKSPACE, page_size=100, show_deleted=True)
    assert len(secrets.secrets) == 6


def assert_list_secrets_pagination(
        secret_client_tested: SecretClient,
):
    # Test no secrets found.
    page = secret_client_tested.list_secrets(parent=DEFAULT_WORKSPACE)
    assert len(page.secrets) == 0
    assert page.next_page_token == ""

    # Arrange
    create_testing_secrets(secret_client_tested)

    # Test getting first page.
    page = secret_client_tested.list_secrets(
        parent=DEFAULT_WORKSPACE,
        page_size=1,
    )
    assert len(page.secrets) == 1
    assert page.next_page_token != ""

    # Test getting second page.
    page = secret_client_tested.list_secrets(
        parent=DEFAULT_WORKSPACE,
        page_size=1,
        page_token=page.next_page_token,
    )
    assert len(page.secrets) == 1
    assert page.next_page_token != ""

    # Test getting last page.
    page = secret_client_tested.list_secrets(
        parent=DEFAULT_WORKSPACE,
        page_size=1,
        page_token=page.next_page_token,
    )
    assert len(page.secrets) == 1
    assert page.next_page_token == ""

    # Test exceeding max page size.
    page = secret_client_tested.list_secrets(
        parent=DEFAULT_WORKSPACE,
        page_size=1001,
    )
    assert len(page.secrets) == 3
    assert page.next_page_token == ""


def create_testing_secrets(secret_client_creator: SecretClient):
    secret_client_creator.create_secret(
        parent=DEFAULT_WORKSPACE,
        secret_id="secret1",
    )
    secret_client_creator.create_secret(
        parent=DEFAULT_WORKSPACE,
        secret_id="secret2",
    )
    secret_client_creator.create_secret(
        parent=DEFAULT_WORKSPACE,
        secret_id="secret3",
    )


def create_testing_secrets_deleted(secret_client_creator: SecretClient):
    s1 = secret_client_creator.create_secret(
        parent=DEFAULT_WORKSPACE,
        secret_id="secret1-delete",
    )
    secret_client_creator.delete_secret(name=s1.name)
    s2 = secret_client_creator.create_secret(
        parent=DEFAULT_WORKSPACE,
        secret_id="secret2-delete",
    )
    secret_client_creator.delete_secret(name=s2.name)
    s3 = secret_client_creator.create_secret(
        parent=DEFAULT_WORKSPACE,
        secret_id="secret3-delete",
    )
    secret_client_creator.delete_secret(name=s3.name)
