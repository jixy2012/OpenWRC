"""
Integration tests for WrcApiClient
Tests all endpoints with real API calls to verify model validation works correctly
"""

from typing import Generator
import pytest
from openwrc.clients.wrc_api_client import WrcApiClient
from openwrc.models.external_api import (
    EventMetadata,
    Itinerary,
)


# Test data
EVENT_ID = 555
RALLY_ID = 603
STAGE_ID = 10279
ITINERARY_ID = 1343


@pytest.fixture
def client() -> Generator[WrcApiClient, None, None]:
    """Create a WrcApiClient instance"""
    yield WrcApiClient()


def test_get_event_metadata(client: WrcApiClient) -> None:
    """Test fetching event metadata"""
    result = client.get_event_metadata(EVENT_ID)

    assert isinstance(result, EventMetadata)
    assert result.event_id == EVENT_ID
    assert len(result.rallies) > 0
    print(f"✓ Event metadata: {result.name}")


def test_get_event_itineraries(client: WrcApiClient) -> None:
    """Test fetching event itineraries"""
    result = client.get_event_itineraries(EVENT_ID, ITINERARY_ID)

    assert isinstance(result, Itinerary)
    assert result.itinerary_id == ITINERARY_ID
    assert len(result.itinerary_legs) > 0
    print(f"✓ Itinerary: {len(result.itinerary_legs)} legs")


def test_get_rally_entries(client: WrcApiClient) -> None:
    """Test fetching rally entries"""
    result = client.get_rally_entries(EVENT_ID, RALLY_ID)

    assert isinstance(result, list)
    assert len(result) > 0
    print(f"✓ Rally entries: {len(result)} entries")


def test_get_rally_results(client: WrcApiClient) -> None:
    """Test fetching rally results"""
    result = client.get_rally_results(EVENT_ID, RALLY_ID)

    assert isinstance(result, list)
    assert len(result) > 0
    # Verify each entry has the required fields
    for entry in result:
        assert hasattr(entry, "entry_id")
        assert hasattr(entry, "stage_time_ms")
        assert hasattr(entry, "total_time_ms")
    print(f"✓ Rally results: {len(result)} entries")


def test_get_event_stage_results(client: WrcApiClient) -> None:
    """Test fetching stage results"""
    result = client.get_event_stage_results(EVENT_ID, STAGE_ID, RALLY_ID)

    assert isinstance(result, list)
    assert len(result) > 0
    # Verify each entry has the required fields
    for entry in result:
        assert hasattr(entry, "entry_id")
        assert hasattr(entry, "stage_time_ms")
    print(f"✓ Stage results: {len(result)} entries")


def test_get_event_stage_time_results(client: WrcApiClient) -> None:
    """Test fetching stage time results"""
    result = client.get_event_stage_time_results(EVENT_ID, STAGE_ID, RALLY_ID)

    assert isinstance(result, list)
    assert len(result) > 0
    # Verify each entry has the required fields
    for entry in result:
        assert hasattr(entry, "stage_id")
        assert hasattr(entry, "status")
        assert entry.stage_id == STAGE_ID
    print(f"✓ Stage time results: {len(result)} entries")


def test_all_endpoints_integration(client: WrcApiClient) -> None:
    """Integration test that exercises all endpoints in sequence"""
    print("\n=== Running full integration test ===")

    # 1. Get event metadata
    event = client.get_event_metadata(EVENT_ID)
    print(f"1. Event: {event.name} ({event.event_id})")

    # 2. Get itinerary
    itinerary = client.get_event_itineraries(EVENT_ID, ITINERARY_ID)
    print(f"2. Itinerary: {len(itinerary.itinerary_legs)} legs")

    # 3. Get rally entries
    entries = client.get_rally_entries(EVENT_ID, RALLY_ID)
    print(f"3. Entries: {len(entries)} drivers")

    # 4. Get rally results
    rally_results = client.get_rally_results(EVENT_ID, RALLY_ID)
    print(f"4. Rally results: {len(rally_results)} entries")

    # 5. Get stage results
    stage_results = client.get_event_stage_results(EVENT_ID, STAGE_ID, RALLY_ID)
    print(f"5. Stage results: {len(stage_results)} entries")

    # 6. Get stage time results
    stage_times = client.get_event_stage_time_results(EVENT_ID, STAGE_ID, RALLY_ID)
    print(f"6. Stage time results: {len(stage_times)} entries")

    print("=== All endpoints working correctly ===\n")
