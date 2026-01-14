import uuid
from datetime import datetime
from datetime import timezone

import urllib3
from urllib3.exceptions import InsecureRequestWarning

import h2o_audit_trail
from h2o_audit_trail.event.create import CreateEventRequest
from h2o_audit_trail.event.event import Event
from h2o_audit_trail.event.search import SearchEventsRequestFilter
from h2o_audit_trail.model.status import Status

# We don't want to display warning messages:
# "InsecureRequestWarning: Unverified HTTPS request is being made to host 'audittrail.cloud-dev.h2o.dev' ... "
urllib3.disable_warnings(InsecureRequestWarning)

event_client = h2o_audit_trail.login_custom(
    endpoint="https://audittrail.cloud-dev.h2o.dev",
    # Pass in a valid platform token for cloud-dev.
    refresh_token="<PLATFORM_TOKEN>",
    issuer_url="https://auth.cloud-dev.h2o.dev/auth/realms/hac",
    client_id="hac-platform-public",
    verify_ssl=False,
).event_client

start_time = datetime.now(timezone.utc)
event1_id = str(uuid.uuid4())
event2_id = str(uuid.uuid4())
event3_id = str(uuid.uuid4())
event4_id = str(uuid.uuid4())

# Create one event.
event = event_client.create_event(
    event_id=event1_id,
    event=Event(
        event_time=datetime.now(timezone.utc),
        event_source="h2oai-enginemanager-server",
        action="actions/enginemanager/daiEngines/CREATE",
        read_only=False,
        status=Status(
            code=0,
        ),
        principal="users/jans",
        source_ip_address="1.1.1.1",
        metadata={"display_name": "event1"},
    ),
)
print(f"created {event.metadata["display_name"]} ({event.name})")

# Create multiple events in one request. Supports partial failure.
batch_resp = event_client.batch_create_events(
    requests=[
        CreateEventRequest(
            event_id=event2_id,
            event=Event(
                event_time=datetime.now(timezone.utc),
                event_source="h2oai-enginemanager-server",
                action="actions/enginemanager/daiEngines/CREATE",
                read_only=False,
                status=Status(
                    code=0,
                ),
                principal="users/jans",
                source_ip_address="1.1.1.1",
                metadata={"display_name": "event2"},
            ),
        ),
        CreateEventRequest(
            event_id=event3_id,
            event=Event(
                event_time=datetime.now(timezone.utc),
                event_source="h2oai-enginemanager-server",
                action="actions/enginemanager/daiEngines/CREATE",
                read_only=False,
                status=Status(
                    code=0,
                ),
                principal="users/foo",
                source_ip_address="1.1.1.1",
                metadata={"display_name": "event3"},
            ),
        ),
        CreateEventRequest(
            event_id=event4_id,
            event=Event(
                event_time=datetime.now(timezone.utc),
                event_source="h2oai-enginemanager-server",
                action="actions/enginemanager/daiEngines/CREATE",
                read_only=False,
                status=Status(
                    code=0,
                ),
                principal="users/jans",
                source_ip_address="1.1.1.1",
                metadata={"display_name": "event4"},
            ),
        ),
    ],
)

print(f"batch created {len(batch_resp.events)} event(s)")
for event in batch_resp.events:
    print(f"\tcreated {event.metadata["display_name"]} ({event.name})")

print(f"failed to batch create {len(batch_resp.failed_requests)} event(s)")
for idx, rpcStatus in batch_resp.failed_requests:
    print(f"\tfailed request on index {idx}: {rpcStatus.code} | {rpcStatus.message}")

# Search for events with principal "users/jans" within a time window [start_time, end_time).
# Using pagination (2 events per page).
end_time = datetime.now(timezone.utc)
page_token = ""
max_pages = 5

for i in range(max_pages):
    search_resp = event_client.search_events(
        filter_=SearchEventsRequestFilter(
            start_event_time=start_time,
            end_event_time=end_time,
            principal_exact="users/jans",
        ),
        page_size=2,
        page_token=page_token,
    )
    print(f"page {i + 1}, got {len(search_resp.events)} event(s):")
    for event in search_resp.events:
        print(f"\t{event.metadata["display_name"]} ({event.name})")

    page_token = search_resp.next_page_token

    print(f"next page available: {'Yes' if page_token else 'No'}")

    if not page_token:
        break
