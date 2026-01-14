from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional

from h2o_audit_trail.event.event import Event
from h2o_audit_trail.event.event_type import EventType
from h2o_audit_trail.event.event_type import event_types_to_api_event_types
from h2o_audit_trail.gen.model.search_events_request_filter import (
    SearchEventsRequestFilter as V1SearchEventsRequestFilter,
)


@dataclass
class SearchEventsRequestFilter:
    start_event_time: Optional[datetime] = None
    """
    Filter events with event_time >= start_event_time. 
    Defaults to 2025-07-01 00:00:00 +0000 UTC.
    """

    end_event_time: Optional[datetime] = None
    """
    Filter events with event_time < end_event_time. 
    Defaults to now.
    """

    event_source_exact: Optional[str] = None
    """Filter events with event_source equal to this value."""

    event_source_regex: Optional[str] = None
    """
    Filter events with event_source matching regex from this value.
    Must follow Google's RE2 syntax.
    """

    resource_exact: Optional[str] = None
    """Filter events with resource equal to this value."""

    resource_regex: Optional[str] = None
    """
    Filter events with resource matching regex from this value.
    Must follow Google's RE2 syntax.
    """

    read_only: Optional[bool] = None
    """Filter events with read_only equal to this value."""

    status_code_regex: Optional[str] = None
    """
    Filter events with status.code that matches regex from this value.
    StatusCodes: 0=OK, 1=CANCELLED, 2=UNKNOWN, 3=INVALID_ARGUMENT, ...
    Filtering events with statusCode OK or INVALID_ARGUMENT can be expressed by regex "^(0|3)$".
    Filtering events with no statusCode can be expressed by regex "^$".
    Must follow Google's RE2 syntax
    """

    principal_exact: Optional[str] = None
    """Filter events with principal equal to this value."""

    principal_regex: Optional[str] = None
    """
    Filter events with principal matching regex from this value.
    Must follow Google's RE2 syntax.
    """

    source_ip_address_exact: Optional[str] = None
    """Filter events with source_ip_address equal to this value."""

    source_ip_address_regex: Optional[str] = None
    """
    Filter events with source_ip_address matching regex from this value.
    Must follow Google's RE2 syntax.
    """

    metadata_exact: Dict[str, str] = field(default_factory=dict)
    """
    Filter events that contain in its metadata the same key-value pairs.
    For example, if metadata_exact={"a":"b", "c":"d"} then each returned event must contain in its metadata
    key "a" with value "b" and key "c" with value "d".
    Empty map implies no filtering by metadata is applied.
    """

    metadata_regex: Dict[str, str] = field(default_factory=dict)
    """
    Optional. Filter events that contain in its metadata keys with values matching a regex.
    For example, if metadata_regex={"a":".*b.*", "c":".*d.*"} then each returned event must contain in its metadata
    key "a" with value that "contains letter b" and key "c" with value that "contains letter d".
    Empty map implies no filtering by metadata is applied.
    Values must follow Google's RE2 syntax.
    """

    workspace_exact: Optional[str] = None
    """Filter events with workspace equal to this value."""

    workspace_regex: Optional[str] = None
    """
    Filter events with workspace matching regex from this value.
    Must follow Google's RE2 syntax.
    """

    action_exact: Optional[str] = None
    """Filter events with action equal to this value."""

    action_regex: Optional[str] = None
    """
    Filter events with action matching regex from this value.
    Must follow Google's RE2 syntax.
    """

    include_types: List[EventType] = field(default_factory=list)
    """
    Filter events by type.
    When multiple types are specified, events matching any of the types are returned.
    Empty list implies no filtering by type is applied.
    Example: include_types = [EventType.TYPE_API] returns only events with type TYPE_API.
    """

    exclude_types: List[EventType] = field(default_factory=list)
    """
    Exclude events by type.
    When multiple types are specified, events matching any of the types are excluded.
    Empty list implies no exclusion by type is applied.
    Example: exclude_types = [EventType.TYPE_API, EventType.TYPE_SYSTEM] returns events
    that are neither TYPE_API nor TYPE_SYSTEM.
    """


@dataclass
class SearchEventsResponse:
    events: List[Event]
    """Searched events."""

    next_page_token: str
    """
    Used to retrieve the next page of results.
    When unset (empty string), no further items are available (this response was the last page).
    """

    searched_until_time: datetime
    """
    The point in time that the backwards search has progressed to.
    
    This field is for informational purposes ONLY to indicate search progress.
    It MUST NOT be used to construct the next search request.
    Always use the 'next_page_token' for subsequent page requests.
    
    Example:
        For a search from a start_event_time of 'July 1st 00:00:00' to an end_event_time of 'July 10th 00:00:00',
        the search proceeds backwards from July 10th (exclusive). If this field returns
        'July 5th 00:00:00', it means the time range [July 5th, July 10th) has been scanned.
    """


def search_events_request_filter_to_api(filter_: Optional[SearchEventsRequestFilter]) -> V1SearchEventsRequestFilter:
    if filter_ is None:
        return V1SearchEventsRequestFilter()

    return V1SearchEventsRequestFilter(
        start_event_time=filter_.start_event_time,
        end_event_time=filter_.end_event_time,
        event_source_exact=filter_.event_source_exact,
        event_source_regex=filter_.event_source_regex,
        resource_exact=filter_.resource_exact,
        resource_regex=filter_.resource_regex,
        read_only=filter_.read_only,
        status_code_regex=filter_.status_code_regex,
        principal_exact=filter_.principal_exact,
        principal_regex=filter_.principal_regex,
        source_ip_address_exact=filter_.source_ip_address_exact,
        source_ip_address_regex=filter_.source_ip_address_regex,
        metadata_exact=filter_.metadata_exact,
        metadata_regex=filter_.metadata_regex,
        workspace_exact=filter_.workspace_exact,
        workspace_regex=filter_.workspace_regex,
        action_exact=filter_.action_exact,
        action_regex=filter_.action_regex,
        include_types=event_types_to_api_event_types(filter_.include_types),
        exclude_types=event_types_to_api_event_types(filter_.exclude_types),
    )
