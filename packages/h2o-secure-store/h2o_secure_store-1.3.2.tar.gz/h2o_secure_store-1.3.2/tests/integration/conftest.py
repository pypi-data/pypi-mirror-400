import os

import psycopg2
import pytest as pytest

import h2o_secure_store


@pytest.fixture(scope="session")
def user_clients():
    return h2o_secure_store.login_custom(
        endpoint=os.getenv("SECURE_STORE_SERVER_URL"),
        refresh_token=os.getenv("PLATFORM_TOKEN_USER_ALLOWED"),
        issuer_url=os.getenv("PLATFORM_OIDC_URL"),
        client_id=os.getenv("PLATFORM_OIDC_CLIENT_ID"),
    )

@pytest.fixture(scope="session")
def user_2_clients():
    return h2o_secure_store.login_custom(
        endpoint=os.getenv("SECURE_STORE_SERVER_URL"),
        refresh_token=os.getenv("PLATFORM_TOKEN_USER_ALLOWED_2"),
        issuer_url=os.getenv("PLATFORM_OIDC_URL"),
        client_id=os.getenv("PLATFORM_OIDC_CLIENT_ID"),
    )


@pytest.fixture(scope="session")
def db_connection():
    conn_string =os.getenv("POSTGRES_DSN")
    return psycopg2.connect(conn_string)


@pytest.fixture(scope="session")
def user_oauth_client_client(user_clients):
    return user_clients.oauth_client_client


@pytest.fixture(scope="session")
def user_token_source_client(user_clients):
    return user_clients.token_source_client


@pytest.fixture(scope="session")
def user_2_token_source_client(user_2_clients):
    return user_2_clients.token_source_client


@pytest.fixture(scope="session")
def user_secret_client(user_clients):
    return user_clients.secret_client


@pytest.fixture(scope="session")
def user_2_secret_client(user_2_clients):
    return user_2_clients.secret_client


@pytest.fixture(scope="session")
def user_allowed_secret_version_client(user_clients):
    return user_clients.secret_version_client


@pytest.fixture(scope="function")
def delete_all_oauth_clients_before_after(user_oauth_client_client):
    user_oauth_client_client.delete_all_oauth_clients()
    yield
    user_oauth_client_client.delete_all_oauth_clients()


@pytest.fixture(scope="function")
def delete_all_token_sources_before_after(user_token_source_client, oauth_client1):
    user_token_source_client.delete_all_token_sources(oauth_client_id=oauth_client1.oauth_client_id)
    yield
    user_token_source_client.delete_all_token_sources(oauth_client_id=oauth_client1.oauth_client_id)


@pytest.fixture(scope="function")
def delete_secret_rows_before(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM secret;")
    db_connection.commit()
    cursor.close()


@pytest.fixture(scope="function")
def secret_user_allowed(user_secret_client):
    return user_secret_client.create_secret(
        parent="workspaces/default",
    )


@pytest.fixture(scope="function")
def oauth_client1(user_oauth_client_client):
    oauth_client = user_oauth_client_client.create_oauth_client(
        issuer="issuer1",
        client_id="client1",
        oauth_client_id="oauth-client1",
        authorization_endpoint="authz-endpoint",
        token_endpoint="token-endpoint",
    )
    yield oauth_client
    user_oauth_client_client.delete_oauth_client(oauth_client_id="oauth-client1")


@pytest.fixture(scope="function")
def oauth_client2(user_oauth_client_client):
    oauth_client = user_oauth_client_client.create_oauth_client(
        issuer="issuer1",
        client_id="client2",
        oauth_client_id="oauth-client2",
        authorization_endpoint="authz-endpoint",
        token_endpoint="token-endpoint",
    )
    yield oauth_client
    user_oauth_client_client.delete_oauth_client(oauth_client_id="oauth-client2")


@pytest.fixture(scope="function")
def oauth_client3(user_oauth_client_client):
    oauth_client = user_oauth_client_client.create_oauth_client(
        issuer="issuer1",
        client_id="client3",
        oauth_client_id="oauth-client3",
        authorization_endpoint="authz-endpoint",
        token_endpoint="token-endpoint",
    )
    yield oauth_client
    user_oauth_client_client.delete_oauth_client(oauth_client_id="oauth-client3")


@pytest.fixture(scope="function")
def token_source1(user_token_source_client, oauth_client1):
    token_source = user_token_source_client.create_token_source(
        oauth_client_id=oauth_client1.oauth_client_id,
        redirect_uri="http://localhost:8080",
        token_source_id="token-source1",
    )
    yield token_source
    user_token_source_client.delete_token_source(
        token_source_id="token-source1", oauth_client_id=oauth_client1.oauth_client_id
    )


@pytest.fixture(scope="function")
def token_source2(user_token_source_client, oauth_client1):
    token_source = user_token_source_client.create_token_source(
        oauth_client_id=oauth_client1.oauth_client_id,
        redirect_uri="http://localhost:8080",
        token_source_id="token-source2",
    )
    yield token_source
    user_token_source_client.delete_token_source(
        token_source_id="token-source2", oauth_client_id=oauth_client1.oauth_client_id
    )


@pytest.fixture(scope="function")
def token_source3(user_token_source_client, oauth_client1):
    token_source = user_token_source_client.create_token_source(
        oauth_client_id=oauth_client1.oauth_client_id,
        redirect_uri="http://localhost:8080",
        token_source_id="token-source3",
    )
    yield token_source
    user_token_source_client.delete_token_source(
        token_source_id="token-source3", oauth_client_id=oauth_client1.oauth_client_id
    )