import datetime
import http
import time

import pytest

from h2o_secure_store.clients.base.workspace import DEFAULT_WORKSPACE
from h2o_secure_store.clients.secret.client import SecretClient
from h2o_secure_store.clients.secret_version.client import SecretVersionClient
from h2o_secure_store.clients.secret_version.secret_version import SecretVersion
from h2o_secure_store.exception import CustomApiException


def test_prune_deleted_secret(
        delete_secret_rows_before,
        user_secret_client: SecretClient,
        user_allowed_secret_version_client: SecretVersionClient,
):
    s = user_secret_client.create_secret(
        parent=DEFAULT_WORKSPACE,
        secret_id="secret1",
    )

    v = user_allowed_secret_version_client.create_secret_version(
        parent=s.name,
        secret_version=SecretVersion(
            value=b"secret1",
        ),
    )

    deleted = user_secret_client.delete_secret(name=s.name)
    now_utc = datetime.datetime.now(tz=datetime.timezone.utc)

    assert deleted.purge_time.astimezone(datetime.timezone.utc) > now_utc
    assert deleted.purge_time.astimezone(datetime.timezone.utc) < now_utc + datetime.timedelta(seconds=5)

    # Wait for the secret to be pruned, reconciliation every 2s + 2s for the prune duration
    time.sleep(5)

    with pytest.raises(CustomApiException) as exc:
        user_secret_client.get_secret(name=deleted.name)
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    with pytest.raises(CustomApiException) as exc:
        user_allowed_secret_version_client.get_secret_version(name=v.name)
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

