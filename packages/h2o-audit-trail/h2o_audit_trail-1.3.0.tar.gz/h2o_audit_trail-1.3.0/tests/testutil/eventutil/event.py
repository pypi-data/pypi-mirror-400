from datetime import datetime
from datetime import timezone
from typing import Callable
from typing import Dict

from h2o_audit_trail.event.event import Event
from h2o_audit_trail.model.status import Status

Option = Callable[[Event], None]


def with_event_time(event_time: datetime) -> Option:
    """Returns an option to set the event_time."""

    def option(event: Event) -> None:
        event.event_time = event_time

    return option


def with_read_only(read_only: bool) -> Option:
    """Returns an option to set the read_only flag."""

    def option(event: Event) -> None:
        event.read_only = read_only

    return option


def with_status(status: Status) -> Option:
    """Returns an option to set the status."""

    def option(event: Event) -> None:
        event.status = status

    return option


def with_principal(principal: str) -> Option:
    """Returns an option to set the principal."""

    def option(event: Event) -> None:
        event.principal = principal

    return option


def with_event_source(event_source: str) -> Option:
    def option(event: Event) -> None:
        event.event_source = event_source

    return option


def with_resource(resource: str) -> Option:
    def option(event: Event) -> None:
        event.resource = resource

    return option


def with_action(action: str) -> Option:
    def option(event: Event) -> None:
        event.action = action

    return option


def with_source_ip_address(source_ip_address: str) -> Option:
    def option(event: Event) -> None:
        event.source_ip_address = source_ip_address

    return option


def with_metadata(metadata: Dict[str, str]) -> Option:
    def option(event: Event) -> None:
        event.metadata = metadata

    return option


def with_request_parameters(request_parameters: Dict[str, str]) -> Option:
    def option(event: Event) -> None:
        event.request_parameters = request_parameters

    return option


def with_user_agent(user_agent: str) -> Option:
    def option(event: Event) -> None:
        event.user_agent = user_agent

    return option


def default_event(*opts: Option) -> Event:
    event = Event(
        event_time=datetime.now(timezone.utc),
        event_source="h2oai-enginemanager-server",
        action="actions/enginemanager/daiEngines/CREATE",
        read_only=False,
        principal="users/jans",
        source_ip_address="1.1.1.1",
        status=Status(
            code=3,
            message="cpu must be < 5",
        )
    )

    for opt in opts:
        opt(event)

    return event
