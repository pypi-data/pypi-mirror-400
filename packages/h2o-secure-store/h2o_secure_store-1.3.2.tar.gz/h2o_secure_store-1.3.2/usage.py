# pip install https://secure-store-release.s3.amazonaws.com/latest-snapshot/downloads/h2o_secure_store-0.1.0-py3-none-any.whl
import h2o_secure_store

# This will work only when running in Notebook Lab or locally if you have H2O CLI configured.
# Otherwise you need to pass additional arguments to the login function.
# See the login function docstring for more information.
hss = h2o_secure_store.login()

# Administrator set-up.
# This part needs to be done once, as an administrator.
# It registers an OAuth client with the Secure Store.

# List existing clients to see if the client already exists.
hss.oauth_client_client.list_all_oauth_clients()

# Create a new OAuth client
snowflake_client = hss.oauth_client_client.create_oauth_client(
    display_name="Snowflake",
    issuer="https://dev-41714738.okta.com/oauth2/aush3dnts4AA4K0C85d7",
    client_id="0oah7v0o13gI1Peec5d7",
    client_secret="5rDBGiMbEHE1YN-nFzWAxiGAKf9Jmg5M1VLofcOAdHIyBJn2wgkvy1rxDoM4GhRU",
    extra_scopes=["profile", "email"],  # Strongly recommended. Do not include the openid or offline_access scopes here.
    refresh_disabled=False,  # Enable only when the offline_access scope is not granted.
    login_principal_claim="preferred_username"  # The ID Token claim that contains the "username".
)

# When created, there will be a callback_uri that needs to be added in the IDP as a valid redirect URI.
print(f"Callback URI: {snowflake_client.callback_uri}")

# Delete the OAuth client all it's child TokenSources.
# hss.oauth_client_client.delete_oauth_client(snowflake_client.oauth_client_id)

####################################################################################################
# End user portion

# List existing OAuth clients and let user to chose one.
oauth_clients = hss.oauth_client_client.list_all_oauth_clients()

# We will use the first client for this example.
oauth_client = oauth_clients[0]

# Create a new TokenSource under the existing OAuth client.
# You can optionally specify a redirect_uri where the user will be redirected after successful login.
# That can be useful for callback to the application, so it knows to fetch the newly populated token.
ts = hss.token_source_client.create_token_source(
    oauth_client_id=oauth_client.oauth_client_id,
    # redirect_uri="https://h2o.ai",  # Optional.
)

# The user must now visit this URL.
print(f"Visit this URL: {ts.login_uri}")

# When you know user has logged in, re-fetch the TokenSource.
# You can also poll if callback is not an option.
ts = hss.token_source_client.get_token_source(
    oauth_client_id=oauth_client.oauth_client_id,
    token_source_id=ts.token_source_id,
)

print(f"Token: {ts.access_token}")
print(f"Expiration: {ts.expire_time}")

# The token source will keep refreshing the token in the background as long as possible.
# Come back and re-fetch the TokenSource at expire_time.

ts = hss.token_source_client.get_token_source(
    oauth_client_id=oauth_client.oauth_client_id,
    token_source_id=ts.token_source_id,
)

# If refresh token was revoked, or we cannot refresh the token for some reason,
# the TokenSource.login_required flag will be set to True and you must direct user to
# the login_uri again.
if ts.login_required:
    print(f"Login required: {ts.login_required}")
    print(f"Visit this URL: {ts.login_uri}")
else:
    print(f"Token: {ts.access_token}")
    print(f"Expiration: {ts.expire_time}")

# You can also list existing token sources.
hss.token_source_client.list_all_token_sources(oauth_client_id=oauth_client.oauth_client_id)

# You can also delete the TokenSource.
hss.token_source_client.delete_token_source(
    oauth_client_id=oauth_client.oauth_client_id,
    token_source_id=ts.token_source_id,
)
