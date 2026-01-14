import time
from datetime import datetime
from datetime import timezone

from h2o_audit_trail.event.client import EventClient
from h2o_audit_trail.event.search import SearchEventsRequestFilter


def test_internal_audit(event_client_user4: EventClient) -> None:
    start = datetime.now(tz=timezone.utc)
    event_client_user4.search_events()
    # Wait a little bit to make sure the internal Search event is created.
    time.sleep(0.5)
    end = datetime.now(tz=timezone.utc)

    resp = event_client_user4.search_events(
        filter_=SearchEventsRequestFilter(
            start_event_time=start,
            event_source_exact="h2oai-audittrail-server",
            action_exact="actions/audittrail/events/SEARCH",
            end_event_time=end,
        )
    )

    assert len (resp.events) == 1
