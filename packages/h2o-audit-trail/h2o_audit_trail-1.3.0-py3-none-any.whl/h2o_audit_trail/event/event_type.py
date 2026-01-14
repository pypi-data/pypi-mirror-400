from enum import Enum
from typing import List

from h2o_audit_trail.gen.model.v1_event_type import V1EventType


class EventType(str, Enum):
    """Classifies the type of event."""

    TYPE_UNSPECIFIED = "TYPE_UNSPECIFIED"
    """Unspecified event type."""

    TYPE_API = "TYPE_API"
    """Event initiated by a user's API request."""

    TYPE_SYSTEM = "TYPE_SYSTEM"
    """Event initiated by system action or automation."""


def event_type_to_api_event_type(event_type: EventType) -> V1EventType:
    return V1EventType(event_type.value)


def event_types_to_api_event_types(event_types: List[EventType]) -> List[V1EventType]:
    return [event_type_to_api_event_type(t) for t in event_types]


def event_type_from_api_event_type(api_event_type: V1EventType) -> EventType:
    return EventType(api_event_type.value)