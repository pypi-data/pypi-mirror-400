from typing import List
from typing import Optional

from h2o_audit_trail.auth.token_api_client import TokenApiClient
from h2o_audit_trail.connection_config import ConnectionConfig
from h2o_audit_trail.event.create import BatchCreateEventsResponse
from h2o_audit_trail.event.create import CreateEventRequest
from h2o_audit_trail.event.create import batch_create_events_response_from_api
from h2o_audit_trail.event.create import create_event_requests_to_api_requests
from h2o_audit_trail.event.event import Event
from h2o_audit_trail.event.event import event_from_api_event
from h2o_audit_trail.event.event import event_to_api_event
from h2o_audit_trail.event.event import events_from_api_events
from h2o_audit_trail.event.search import SearchEventsRequestFilter
from h2o_audit_trail.event.search import SearchEventsResponse
from h2o_audit_trail.event.search import search_events_request_filter_to_api
from h2o_audit_trail.exception import CustomApiException
from h2o_audit_trail.gen import ApiException
from h2o_audit_trail.gen import Configuration
from h2o_audit_trail.gen.api.event_service_api import EventServiceApi
from h2o_audit_trail.gen.model.v1_batch_create_events_request import (
    V1BatchCreateEventsRequest,
)
from h2o_audit_trail.gen.model.v1_batch_create_events_response import (
    V1BatchCreateEventsResponse,
)
from h2o_audit_trail.gen.model.v1_event import V1Event
from h2o_audit_trail.gen.model.v1_search_events_request import V1SearchEventsRequest
from h2o_audit_trail.gen.model.v1_search_events_response import V1SearchEventsResponse


class EventClient:
    """EventClient manages Events."""

    def __init__(
        self,
        connection_config: ConnectionConfig,
        verify_ssl: bool = True,
        ssl_ca_cert: Optional[str] = None,
    ):
        """Initializes EventClient.

        Args:
            connection_config (ConnectionConfig): Audit Trail connection configuration object.
            verify_ssl (bool): Set to False to disable SSL certificate verification.
            ssl_ca_cert (Optional[str]): Path to a CA cert bundle with certificates of trusted CAs.
        """

        configuration = Configuration(host=connection_config.audit_trail_url)
        configuration.verify_ssl = verify_ssl
        configuration.ssl_ca_cert = ssl_ca_cert

        with TokenApiClient(
            configuration, connection_config.token_provider
        ) as api_client:
            self.service_api = EventServiceApi(api_client)

    def create_event(
        self,
        event_id: str,
        event: Event,
    ) -> Event:
        """Creates an Event.

        Args:
            event_id (str): The ID of the Event resource to create.
                Must be a UUID4, for example: "b096430b-c7a8-47f2-a129-d9ae58cf454f".
            event (Event): The Event resource to create.
        Returns:
            Event: created Event.
        """
        created_api_object: V1Event

        try:
            created_api_object = self.service_api.event_service_create_event(
                event_id=event_id,
                event=event_to_api_event(event=event),
            ).event
        except ApiException as e:
            raise CustomApiException(e)

        return event_from_api_event(created_api_object)

    def batch_create_events(
        self,
        requests: List[CreateEventRequest],
    ) -> BatchCreateEventsResponse:
        """Create multiple Events.

        Args:
            requests (List[CreateEventRequest]): A list of objects, where each object describes an event to be created.
                A maximum of 1000 events can be created in a batch.
        Returns:
            BatchCreateEventsResponse: A response object containing successfully created events
                and failed create requests.
        """
        api_requests = create_event_requests_to_api_requests(requests=requests)
        api_resp: V1BatchCreateEventsResponse
        try:
            api_resp = self.service_api.event_service_batch_create_events(
                body=V1BatchCreateEventsRequest(requests=api_requests),
            )
        except ApiException as e:
            raise CustomApiException(e)

        return batch_create_events_response_from_api(api_response=api_resp)

    def search_events(
        self,
        filter_: Optional[SearchEventsRequestFilter] = None,
        page_size: int = 0,
        page_token: str = "",
    ) -> SearchEventsResponse:
        """Search Events.

        Args:
            filter_: Filter for events. When unset, default filter values will be used.
            page_size: Maximum number of Events to return in a response.
                When unset, at most 50 Events will be returned.
                The maximum value is 1000; values above 1000 will be coerced to 1000.
            page_token: Leave unset to receive the initial page.
                To list any subsequent pages, use the value of 'next_page_token'
                returned from the SearchEventsResponse.
        Returns:
            SearchEventsResponse: A response object containing searched events with next_page_token.
        """

        api_resp: V1SearchEventsResponse
        try:
            api_resp = self.service_api.event_service_search_events(
                body=V1SearchEventsRequest(
                    filter=search_events_request_filter_to_api(filter_=filter_),
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        except ApiException as e:
            raise CustomApiException(e)

        return SearchEventsResponse(
            events=events_from_api_events(api_events=api_resp.events),
            next_page_token=api_resp.next_page_token,
            searched_until_time=api_resp.searched_until_time,
        )
