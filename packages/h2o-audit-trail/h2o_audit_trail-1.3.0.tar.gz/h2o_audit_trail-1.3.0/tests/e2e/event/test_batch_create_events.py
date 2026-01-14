import http
import uuid
from datetime import datetime
from datetime import timezone

import pytest

from h2o_audit_trail.event.client import EventClient
from h2o_audit_trail.event.create import CreateEventRequest
from h2o_audit_trail.exception import CustomApiException
from tests.testutil.eventutil.event import default_event
from tests.testutil.eventutil.event import with_event_time
from tests.testutil.eventutil.event import with_metadata
from tests.testutil.eventutil.event import with_request_parameters
from tests.testutil.eventutil.event import with_resource
from tests.testutil.eventutil.event import with_user_agent


def test_batch_create_events(event_client_user4: EventClient) -> None:
    event_time1 = datetime.now(timezone.utc)
    event_time2 = datetime.now(timezone.utc)
    event_id1 = str(uuid.uuid4())
    event_id2 = str(uuid.uuid4())

    requests = [
        CreateEventRequest(
            event_id=event_id1,
            event=default_event(
                with_event_time(event_time1),
                with_resource("workspaces/w1/daiEngine/e1"),
                with_request_parameters({
                    "param1": "val1",
                    "param2": "val2",
                }),
                with_user_agent("Mozilla/5.0"),
                with_metadata({
                    "key1": "v1",
                    "key2": "v2",
                })
            ),
        ),
        CreateEventRequest(
            event_id=event_id2,
            event=default_event(with_event_time(event_time2)),
        ),
        CreateEventRequest(
            event_id="invalid",
            event=default_event(),
        )
    ]

    with pytest.raises(CustomApiException) as exc:
        event_client_user4.batch_create_events(
            requests=requests,
        )
    assert exc.value.status == http.HTTPStatus.METHOD_NOT_ALLOWED

