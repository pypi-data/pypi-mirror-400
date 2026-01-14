import http

import pytest

from h2o_secure_store.exception import CustomApiException


@pytest.mark.parametrize(
    ["page_size", "page_token"],
    [
        (-20, ""),
        (0, "non-existing-token"),
    ],
)
def test_list_oauth_clients_validation(user_oauth_client_client, page_size, page_token):
    with pytest.raises(CustomApiException) as exc:
        user_oauth_client_client.list_oauth_clients(
            page_size=page_size,
            page_token=page_token,
        )
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST


def test_list_oauth_clients_pagination(
    delete_all_oauth_clients_before_after,
    user_oauth_client_client,
    oauth_client1,
    oauth_client2,
    oauth_client3,
):
    # Test getting first page.
    page = user_oauth_client_client.list_oauth_clients(page_size=1)
    assert len(page.oauth_clients) == 1
    assert page.next_page_token != ""

    # Test getting second page.
    page = user_oauth_client_client.list_oauth_clients(
        page_size=1,
        page_token=page.next_page_token,
    )
    assert len(page.oauth_clients) == 1
    assert page.next_page_token != ""

    # Test getting last page.
    # Test getting second page.
    page = user_oauth_client_client.list_oauth_clients(
        page_size=1,
        page_token=page.next_page_token,
    )
    assert len(page.oauth_clients) == 1
    assert page.next_page_token == ""

    # Test exceeding max page size.
    page = user_oauth_client_client.list_oauth_clients(page_size=5000)
    assert len(page.oauth_clients) == 3
    assert page.next_page_token == ""


def test_list_all_oauth_clients(
    delete_all_oauth_clients_before_after,
    user_oauth_client_client,
    oauth_client1,
    oauth_client2,
    oauth_client3,
):
    oauth_clients = user_oauth_client_client.list_all_oauth_clients()
    assert len(oauth_clients) == 3
    assert oauth_clients[0].oauth_client_id == oauth_client3.oauth_client_id
    assert oauth_clients[1].oauth_client_id == oauth_client2.oauth_client_id
    assert oauth_clients[2].oauth_client_id == oauth_client1.oauth_client_id