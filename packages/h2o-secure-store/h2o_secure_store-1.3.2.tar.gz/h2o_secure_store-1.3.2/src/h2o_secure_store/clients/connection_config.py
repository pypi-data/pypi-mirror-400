import ssl
from typing import Callable
from typing import NamedTuple
from typing import Optional

import h2o_authn
import h2o_discovery
from h2o_authn import TokenProvider

# Name of the platform client in the discovery response.
PLATFORM_CLIENT_NAME = "platform"
# Name of the Secure Store API service in the discovery response.
SECURE_STORE_SERVICE_NAME = "secure-store"


class ConnectionConfig(NamedTuple):
    """Object holding connection configuration for the Secure Store API server."""

    server_url: str
    token_provider: Callable[[], str]


def get_connection(
    server_url: str,
    refresh_token: str,
    issuer_url: str,
    client_id: str,
    client_secret: Optional[str],
    verify_ssl: bool,
    ssl_ca_cert: Optional[str],
) -> ConnectionConfig:
    """Creates ConnectionConfig object. Initializes and tests token provider."""
    ssl_context = ssl.create_default_context(cafile=ssl_ca_cert)  # Will use system store if None
    if not verify_ssl:
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    # init token provider
    tp = h2o_authn.TokenProvider(
        issuer_url=issuer_url,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        http_ssl_context=ssl_context,
    )
    # test token refresh
    tp()

    return ConnectionConfig(server_url=server_url, token_provider=tp)


def discover_platform_connection(
        environment_url: Optional[str] = None,
        config_path: Optional[str] = None,
        platform_token: Optional[str] = None,
        token_provider: Optional[TokenProvider] = None,
        ssl_context: Optional[ssl.SSLContext] = None,
) -> ConnectionConfig:
    """Creates ConnectionConfig object by discovering platform connection configuration using h2o_discovery.

    :param environment_url: Override for the URL of the environment passed to the discovery service.
    :param config_path: Override path to the h2o cli config file passed to the discovery service.
    :param platform_token: Platform token. If not provided, the token will be discovered.
    :param token_provider: Token provider. If not provided, the provider will be constructed from the discovered config.
    :param ssl_context: SSL context to use for the discovery client.
    """
    # Discover the Secure Store server URL
    d = h2o_discovery.discover(environment=environment_url, config_path=config_path, ssl_context=ssl_context)

    secure_store_service = d.services.get(SECURE_STORE_SERVICE_NAME)
    if secure_store_service is None:
        raise Exception("Secure Store API service is not registered in discovery service")

    secure_store_url = secure_store_service.uri
    if not secure_store_url:
        raise ConnectionError("Unable to discover Secure Store server URL connection value.")

    # If the token provider is provided, use it to construct the connection config.
    if token_provider is not None:
        # Test token refresh
        token_provider()
        return ConnectionConfig(server_url=secure_store_url, token_provider=token_provider)

    # If the token provider is not provided, construct it from the discovered config.
    if not platform_token:
        platform_client_credentials = d.credentials[PLATFORM_CLIENT_NAME]
        if platform_client_credentials is None:
            raise Exception("Platform client credentials are not available in discovery service")

        platform_token = platform_client_credentials.refresh_token

    if not platform_token:
        raise ValueError(
            "Please set the 'platform_token' argument or configure the H2O CLI."
        )

    # Discover client id
    platform_client = d.clients.get(PLATFORM_CLIENT_NAME)
    if platform_client is None:
        raise Exception("platform client is not registered in discovery service")

    client_id = platform_client.oauth2_client_id
    if not client_id:
        raise ConnectionError(
            "Unable to discover platform oauth2_client_id connection value."
        )

    tp = h2o_authn.TokenProvider(
        issuer_url=d.environment.issuer_url,
        client_id=client_id,
        refresh_token=platform_token,
        http_ssl_context=ssl_context,
    )
    # Test token refresh
    tp()

    return ConnectionConfig(server_url=secure_store_url, token_provider=tp)
