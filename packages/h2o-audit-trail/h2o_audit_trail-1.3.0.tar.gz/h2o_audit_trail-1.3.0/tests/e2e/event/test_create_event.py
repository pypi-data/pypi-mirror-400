import http
import uuid
from datetime import datetime
from datetime import timezone

import pytest

from h2o_audit_trail.event.client import EventClient
from h2o_audit_trail.event.event import Event
from h2o_audit_trail.exception import CustomApiException
from h2o_audit_trail.model.status import Status


def test_create_event_not_allowed(event_client_user4: EventClient) -> None:
    with pytest.raises(CustomApiException) as exc:
        event_client_user4.create_event(
            event_id=str(uuid.uuid4()),
            event=Event(
                event_time=datetime.now(timezone.utc),
                event_source="h2oai-enginemanager-server",
                action="actions/enginemanager/daiEngines/CREATE",
                read_only=False,
                resource="workspaces/w1/daiEngine/e1",
                request_parameters={
                    "param1": "val1",
                    "param2": "val2",
                },
                status=Status(
                    code=3,
                    message="cpu must be < 5",
                ),
                principal="users/jans",
                source_ip_address="1.1.1.1",
                user_agent="Mozilla/5.0",
                metadata={
                    "key1": "v1",
                    "key2": "v2",
                }
            ),
        )
    assert exc.value.status == http.HTTPStatus.METHOD_NOT_ALLOWED