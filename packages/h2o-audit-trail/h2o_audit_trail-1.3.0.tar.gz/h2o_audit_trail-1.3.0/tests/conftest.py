import os

import pytest

import h2o_audit_trail
from h2o_audit_trail.event.client import EventClient
from h2o_audit_trail.login import Clients


@pytest.fixture(scope="session")
def clients_user4() -> Clients:
    return h2o_audit_trail.login_custom(
        endpoint=os.getenv("GRPC_GATEWAY_ADDR"),
        refresh_token=os.getenv("PLATFORM_TOKEN_USER_4"),
        issuer_url=os.getenv("PLATFORM_OIDC_URL"),
        client_id=os.getenv("PLATFORM_OIDC_CLIENT_ID"),
    )


@pytest.fixture(scope="session")
def event_client_user4(clients_user4: Clients) -> EventClient:
    return clients_user4.event_client
