from h2o_secure_store.clients.secret_version.client import SecretVersionClient
from h2o_secure_store.clients.secret_version.secret_version import SecretVersion


def test_create_secret_version(
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

    assert secret_version.name == f"workspaces/{secret_user_allowed.get_workspace_id()}/secrets/{secret_user_allowed.get_secret_id()}/versions/{secret_version.get_secret_version_id()}"
    assert secret_version.value == b""  # Value is not returned in the response.
    assert secret_version.creator != ""
    assert secret_version.create_time is not None
    assert secret_version.uid  != ""


def test_create_secret_version_generate_secret_version_id(
        delete_secret_rows_before,
        secret_user_allowed,
        user_allowed_secret_version_client: SecretVersionClient,
):
    v1 = user_allowed_secret_version_client.create_secret_version(
        parent=secret_user_allowed.name,
        secret_version=SecretVersion(
            value=b"secret_value"
        ),
    )

    v2 = user_allowed_secret_version_client.create_secret_version(
        parent=secret_user_allowed.name,
        secret_version=SecretVersion(
            value=b"secret_value"
        ),
    )

    assert v1.name != v2.name
    assert v1.get_secret_version_id() != v2.get_secret_version_id()

