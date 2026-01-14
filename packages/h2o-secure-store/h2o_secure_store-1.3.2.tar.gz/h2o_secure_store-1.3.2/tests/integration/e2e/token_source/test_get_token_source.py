import http

import pytest

from h2o_secure_store.clients.token_source.client import TokenSourceClient
from h2o_secure_store.clients.token_source.token_source import TokenSource
from h2o_secure_store.exception import CustomApiException


def test_get_token_source(
        delete_all_token_sources_before_after,
        token_source1: TokenSource,
        user_token_source_client: TokenSourceClient,
):
    got_token_source = user_token_source_client.get_token_source(oauth_client_id=token_source1.oauth_client_id,
                                                                 token_source_id=token_source1.token_source_id)

    assert token_source1.name == got_token_source.name
    assert token_source1.token_source_id == got_token_source.token_source_id
    assert token_source1.oauth_client_id == got_token_source.oauth_client_id
    assert token_source1.creator == got_token_source.creator
    assert token_source1.create_time == got_token_source.create_time
    assert token_source1.login_time == got_token_source.login_time
    assert token_source1.login_required == got_token_source.login_required
    assert token_source1.login_uri == got_token_source.login_uri
    assert token_source1.redirect_uri == got_token_source.redirect_uri
    assert token_source1.access_token == got_token_source.access_token
    assert token_source1.issue_time == got_token_source.issue_time
    assert token_source1.expire_time == got_token_source.expire_time
    assert token_source1.subject == got_token_source.subject
    assert token_source1.login_principal == got_token_source.login_principal
    assert token_source1.uid == got_token_source.uid


def test_get_token_source_not_found(
        delete_all_token_sources_before_after,
        token_source1: TokenSource,
        user_token_source_client: TokenSourceClient,
):
    with pytest.raises(CustomApiException) as exc:
        user_token_source_client.get_token_source(
            token_source_id="non-existing", oauth_client_id=token_source1.oauth_client_id
        )

    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    with pytest.raises(CustomApiException) as exc:
        user_token_source_client.get_token_source(
            token_source_id=token_source1.token_source_id, oauth_client_id="non-existing"
        )

    assert exc.value.status == http.HTTPStatus.NOT_FOUND


def test_get_token_source_forbidden(
        delete_all_token_sources_before_after,
        token_source1: TokenSource,
        user_2_token_source_client: TokenSourceClient,
):
    with pytest.raises(CustomApiException) as exc:
        # token_source1 is created with user_token_source_client - different user
        user_2_token_source_client.get_token_source(
            token_source_id=token_source1.token_source_id, oauth_client_id=token_source1.oauth_client_id
        )
    assert exc.value.status == http.HTTPStatus.FORBIDDEN
