import pprint
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional

from h2o_audit_trail.event.event_type import EventType
from h2o_audit_trail.event.event_type import event_type_from_api_event_type
from h2o_audit_trail.event.event_type import event_type_to_api_event_type
from h2o_audit_trail.gen.model.v1_event import V1Event
from h2o_audit_trail.model.status import Status
from h2o_audit_trail.model.status import status_to_api_status


@dataclass
class Event:
    """
    Represents an event that occurred in the system based on an API request.
    """

    event_time: datetime
    """The time when the event occurred."""

    event_source: str
    """The canonical name of the container image where the event occurred.
    It MUST match the agreed HAIC container naming.
    For example, "h2oai-enginemanager-server" or "thirdparty-chainguard-bitnamikeycloak".
    """

    action: str
    """The requested action.
    Where applicable, it MUST match the name of the action registered with AuthZ.
    """

    read_only: bool
    """Whether the action is a read-only operation."""

    status: Status
    """The status of the request.
    Includes the status code and optional error message and details.
    """

    principal: str
    """The identifier of the authenticated principal making the request.
    For example: "users/a2b3b8a6-05c6-47d1-8ae1-774113404975" or "services/appstore".
    """

    source_ip_address: str
    """The IP address that the request was made from.
    For a source from the Internet, this will be the public IPv4 or IPv6 address.
    Private IP addresses will be redacted to "private".
    """

    name: str = ""
    """Resource name. Format: events/{event}"""

    login_principal: str = ""
    """Unique user-friendly identifier of the User typically used for the authentication.
    The values is taken at the search event time.
    """

    receive_time: Optional[datetime] = None
    """The time when the event was received."""

    resource: str = ""
    """ The target of the request, specified as a full resource name or a collection name.
    Must be a scheme-less URI followed by the relative name.
    For example:
    - Single resource: "//engine-manager/workspaces/8dcc8393-7b39-45f8-9f85-d1978adba483/daiEngines/new-dai-engine-7268"
    - Collection: "//engine-manager/workspaces/8dcc8393-7b39-45f8-9f85-d1978adba483/daiEngines"
    All aliases must be fully resolved. For example "//engine-manager/workspaces/default" is not allowed.
    """

    request_parameters: Dict[str, str] = field(default_factory=dict)
    """The parameters, if any, that were sent with the request.
    May not include all request parameters, such as those that are too large,
    privacy-sensitive, or duplicated elsewhere in the event.
    """

    user_agent: str = ""
    """The agent through which the request was made."""

    metadata: Dict[str, str] = field(default_factory=dict)
    """Other service-specific data about the request, response, and other
    information associated with the current event.
    The key must:
    - contain 1-63 characters
    - contain only lowercase alphanumeric characters or underscore ('_')
    - start with an alphabetic character
    - end with an alphanumeric character
    """

    workspace: str = ""
    """Name of workspace to which the event is related to.
    Format: "workspaces/*".
    When event is related to no workspace, then this field is unset (empty string).
    Workspace can be derived from other fields.
    For example, if resource="workspaces/w1/daiEngines/e1", then workspace="workspaces/w1".
    """

    type: EventType = EventType.TYPE_API
    """Classifies the type of event."""

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def event_to_api_event(event: Event) -> V1Event:
    return V1Event(
        event_time=event.event_time,
        event_source=event.event_source,
        action=event.action,
        read_only=event.read_only,
        status=status_to_api_status(status=event.status),
        principal=event.principal,
        source_ip_address=event.source_ip_address,
        resource=event.resource,
        request_parameters=event.request_parameters,
        user_agent=event.user_agent,
        metadata=event.metadata,
        type=event_type_to_api_event_type(event.type),
    )


def event_from_api_event(api_object: V1Event) -> Event:
    return Event(
        event_time=api_object.event_time,
        event_source=api_object.event_source,
        action=api_object.action,
        read_only=api_object.read_only,
        status=api_object.status,
        principal=api_object.principal,
        source_ip_address=api_object.source_ip_address,
        name=api_object.name,
        receive_time=api_object.receive_time,
        resource=api_object.resource,
        request_parameters=api_object.request_parameters,
        user_agent=api_object.user_agent,
        metadata=api_object.metadata,
        workspace=api_object.workspace,
        login_principal=api_object.login_principal,
        type=event_type_from_api_event_type(api_object.type),
    )


def events_from_api_events(api_events: List[V1Event]) -> List[Event]:
    return [event_from_api_event(api_object=api_object) for api_object in api_events]
