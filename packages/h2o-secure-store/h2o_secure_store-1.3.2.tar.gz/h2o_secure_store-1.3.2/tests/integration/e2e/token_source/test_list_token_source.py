import http

import pytest

from h2o_secure_store.clients.oauth_client.oauth_client import OAuthClient
from h2o_secure_store.clients.token_source.client import TokenSourceClient
from h2o_secure_store.exception import CustomApiException


@pytest.mark.parametrize(
    ["page_size", "page_token"],
    [
        (-20, ""),
        (0, "non-existing-token"),
    ],
)
def test_list_token_sources_validation(
        oauth_client1: OAuthClient,
        user_token_source_client: TokenSourceClient,
        page_size,
        page_token
):
    with pytest.raises(CustomApiException) as exc:
        user_token_source_client.list_token_sources(
            oauth_client_id=oauth_client1.oauth_client_id,
            page_size=page_size,
            page_token=page_token,
        )
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST


def test_list_token_sources_pagination(
        delete_all_token_sources_before_after,
        user_token_source_client: TokenSourceClient,
        token_source1,
        token_source2,
        token_source3,
):
    # Test getting first page.
    page = user_token_source_client.list_token_sources(oauth_client_id=token_source1.oauth_client_id, page_size=1)
    assert len(page.token_sources) == 1
    assert page.next_page_token != ""

    # Test getting second page.
    page = user_token_source_client.list_token_sources(
        oauth_client_id=token_source1.oauth_client_id,
        page_size=1,
        page_token=page.next_page_token,
    )
    assert len(page.token_sources) == 1
    assert page.next_page_token != ""

    # Test getting last page.
    # Test getting second page.
    page = user_token_source_client.list_token_sources(
        oauth_client_id=token_source1.oauth_client_id,
        page_size=1,
        page_token=page.next_page_token,
    )
    assert len(page.token_sources) == 1
    assert page.next_page_token == ""

    # Test exceeding max page size.
    page = user_token_source_client.list_token_sources(oauth_client_id=token_source1.oauth_client_id, page_size=5000)
    assert len(page.token_sources) == 3
    assert page.next_page_token == ""


def test_list_all_token_sources(
        delete_all_token_sources_before_after,
        user_token_source_client: TokenSourceClient,
        token_source1,
        token_source2,
        token_source3,
):
    token_sources = user_token_source_client.list_all_token_sources(oauth_client_id=token_source1.oauth_client_id)
    assert len(token_sources) == 3
    assert token_sources[0].token_source_id == token_source3.token_source_id
    assert token_sources[1].token_source_id == token_source2.token_source_id
    assert token_sources[2].token_source_id == token_source1.token_source_id


def test_list_token_sources_not_owned(
        delete_all_token_sources_before_after,
        user_2_token_source_client: TokenSourceClient,
        token_source1,
):
    # token_source1 is created with user_token_source_client - different user
    token_sources = user_2_token_source_client.list_all_token_sources(oauth_client_id=token_source1.oauth_client_id)
    assert len(token_sources) == 0
