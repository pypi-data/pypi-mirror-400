from dataclasses import dataclass
from typing import Dict
from typing import List

from h2o_audit_trail.event.event import Event
from h2o_audit_trail.event.event import event_to_api_event
from h2o_audit_trail.event.event import events_from_api_events
from h2o_audit_trail.gen.model.googlerpc_status import GooglerpcStatus
from h2o_audit_trail.gen.model.v1_batch_create_events_response import (
    V1BatchCreateEventsResponse,
)
from h2o_audit_trail.gen.model.v1_create_event_request import V1CreateEventRequest
from h2o_audit_trail.model.rpc_status import RPCStatus
from h2o_audit_trail.model.rpc_status import rpc_status_from_google_rpc_status


@dataclass
class CreateEventRequest:
    """Request message for CreateEvent."""

    event_id: str
    """
    The ID of the Event resource to create.
    Must be a UUID4, for example: "b096430b-c7a8-47f2-a129-d9ae58cf454f".
    """

    event: Event
    """The Event resource to create."""


def create_event_requests_to_api_requests(requests: List[CreateEventRequest]) -> List[V1CreateEventRequest]:
    return [create_event_request_to_api_request(request=request) for request in requests]


def create_event_request_to_api_request(request: CreateEventRequest) -> V1CreateEventRequest:
    return V1CreateEventRequest(
        event_id=request.event_id,
        event=event_to_api_event(event=request.event),
    )


@dataclass
class BatchCreateEventsResponse:
    """Response message for BatchCreateEvents."""

    events: List[Event]
    """Successfully created Events."""

    failed_requests: Dict[int, RPCStatus]
    """
    A dictionary for failed requests, mapping the original 
    request's index to an `RPCStatus` object detailing the error.
    """


def batch_create_events_response_from_api(api_response: V1BatchCreateEventsResponse) -> BatchCreateEventsResponse:
    created_events = events_from_api_events(api_events=api_response.events)
    failed_requests = failed_requests_from_api(api_failed_requests=api_response.failed_requests)

    return BatchCreateEventsResponse(
        events=created_events,
        failed_requests=failed_requests,
    )


def failed_requests_from_api(
    api_failed_requests: Dict[str, GooglerpcStatus]
) -> Dict[int, RPCStatus]:
    return {
        int(index_str): rpc_status_from_google_rpc_status(google_rpc_status=google_rpc_status)
        for index_str, google_rpc_status in api_failed_requests.items()
    }
