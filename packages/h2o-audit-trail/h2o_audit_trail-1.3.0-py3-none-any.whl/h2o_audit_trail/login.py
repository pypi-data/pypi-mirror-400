import ssl
from typing import Optional
from typing import Union
from urllib.parse import urljoin

import requests
from h2o_authn import TokenProvider

from h2o_audit_trail.connection_config import ConnectionConfig
from h2o_audit_trail.connection_config import discover_platform_connection
from h2o_audit_trail.connection_config import get_connection
from h2o_audit_trail.event.client import EventClient


class Clients:
    def __init__(
        self,
        event_client: EventClient,
    ) -> None:
        self.event_client = event_client


def login(
    environment: Optional[str] = None,
    token_provider: Optional[TokenProvider] = None,
    platform_token: Optional[str] = None,
    config_path: Optional[str] = None,
    verify_ssl: bool = True,
    ssl_ca_cert: Optional[str] = None,
) -> Clients:
    """Initializes Audit Trail clients for H2O AI Cloud.

    All arguments are optional. Configuration-less login is dependent on having the H2O CLI configured.
    See: https://docs.h2o.ai/h2o-ai-cloud/developerguide/cli#platform-token
    The Discovery Service is used to discover the Engine Manager service endpoint.
    See: https://pypi.org/project/h2o-cloud-discovery/

    Args:
        environment (str, optional): The H2O Cloud environment URL to use (e.g. https://cloud.h2o.ai).
            If left empty, the environment will be read from the H2O CLI configuration or environmental variables.
            Then, h2o-cloud-discovery will be used to discover the Engine Manager service endpoint.
        token_provider (TokenProvider, optional) = Token provider. Takes priority over platform_token argument.
        platform_token (str, optional): H2O Platform Token.
            If neither 'token_provider' nor 'platform_token' is provided the platform token will be read
            from the H2O CLI configuration.
        config_path: (str, optional): Path to the H2O AI Cloud configuration file.
            Defaults to '~/.h2oai/h2o-cli-config.toml'.
        verify_ssl: Set to False to disable SSL certificate verification.
        ssl_ca_cert: Path to a CA cert bundle with certificates of trusted CAs.

    Raises:
        FileNotFoundError: When the H2O CLI configuration file is needed but cannot be found.
        TomlDecodeError: When the H2O CLI configuration file is needed but cannot be processed.
        LookupError: When the service endpoint cannot be discovered.
        ConnectionError: When a communication with server failed.
    """
    ssl_context = ssl.create_default_context(cafile=ssl_ca_cert)  # Will use system store if None
    if not verify_ssl:
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    cfg = discover_platform_connection(
        environment_url=environment,
        platform_token=platform_token,
        token_provider=token_provider,
        config_path=config_path,
        ssl_context=ssl_context,
    )

    return __init_clients(cfg=cfg, verify_ssl=verify_ssl, ssl_ca_cert=ssl_ca_cert)


def login_custom(
    endpoint: str,
    refresh_token: str,
    issuer_url: str,
    client_id: str,
    client_secret: Optional[str] = None,
    verify_ssl: bool = True,
    ssl_ca_cert: Optional[str] = None,
) -> Clients:
    """Initializes Audit Trail clients.

    Args:
        endpoint (str): The Audit Trail service endpoint URL (e.g. https://audittrail.cloud.h2o.ai).
        refresh_token (str): The OIDC refresh token.
        issuer_url (str): The OIDC issuer URL.
        client_id (str): The OIDC Client ID that issued the 'refresh_token'.
        client_secret (str, optional): Optional OIDC Client Secret that issued the 'refresh_token'. Defaults to None.
        verify_ssl: Set to False to disable SSL certificate verification.
        ssl_ca_cert: Path to a CA cert bundle with certificates of trusted CAs.
    """
    # Remove trailing slash from the URL for the generated clients
    endpoint = endpoint.rstrip("/")
    cfg = get_connection(
        audit_trail_url=endpoint,
        refresh_token=refresh_token,
        issuer_url=issuer_url,
        client_id=client_id,
        client_secret=client_secret,
        verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )

    return __init_clients(cfg=cfg, verify_ssl=verify_ssl, ssl_ca_cert=ssl_ca_cert)


def __init_clients(
    cfg: ConnectionConfig,
    verify_ssl: bool,
    ssl_ca_cert: Optional[str],
):
    # Verify that the server is reachable
    version_url = urljoin(cfg.audit_trail_url, "version")

    verify_param: Union[bool, str]
    if verify_ssl:
        verify_param = True
        if ssl_ca_cert:
            verify_param = ssl_ca_cert
    else:
        verify_param = False

    resp = requests.get(version_url, verify=verify_param)
    if not (200 <= resp.status_code <= 299):
        raise ConnectionError(
            f"Server is not reachable. Status code: {resp.status_code}, Response body: {resp.text}"
        )

    event_client = EventClient(
        connection_config=cfg,
        verify_ssl=verify_ssl,
        ssl_ca_cert=ssl_ca_cert,
    )

    return Clients(event_client=event_client)
