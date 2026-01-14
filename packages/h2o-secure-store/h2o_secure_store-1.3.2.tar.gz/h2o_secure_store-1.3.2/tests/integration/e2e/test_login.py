import os

import h2o_authn

import h2o_secure_store


def test_login_custom_with_token_provider():
    tp = h2o_authn.TokenProvider(
        issuer_url=os.getenv("PLATFORM_OIDC_URL"),
        refresh_token=os.getenv("PLATFORM_TOKEN_USER_ALLOWED"),
        client_id=os.getenv("PLATFORM_OIDC_CLIENT_ID"),
    )
    h2o_secure_store.login_custom_with_token_provider(
        endpoint=os.getenv("SECURE_STORE_SERVER_URL"),
        token_provider=tp,
    )
