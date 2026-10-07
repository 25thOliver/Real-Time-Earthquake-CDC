import os
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from ingestion.models import EarthquakeEvent
from ingestion.fetcher import fetch_events_updated_after
from ingestion.schema import schemas


def test_earthquake_event_instantiation():
    event = EarthquakeEvent(
        id="us7000abcd",
        time_ms=1600000000000,
        updated_ms=1600000060000,
        mag=5.4,
        place="10 km NW of Somewhere",
        url="https://earthquake.usgs.gov/earthquakes/eventpage/us7000abcd",
        detail="https://earthquake.usgs.gov/fdsnws/event/1/query?eventid=us7000abcd",
        longitude=-122.1,
        latitude=37.4,
        depth=10.0,
    )
    assert event.id == "us7000abcd"
    assert event.mag == 5.4
    assert event.updated_ms == 1600000060000


@patch("ingestion.fetcher.requests.get")
def test_fetch_events_updated_after_success(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "features": [
            {
                "id": "us1000test",
                "properties": {
                    "time": 1700000000000,
                    "updated": 1700000100000,
                    "mag": 4.2,
                    "place": "Test Region",
                    "url": "http://test.url",
                    "detail": "http://test.detail",
                },
                "geometry": {
                    "coordinates": [-118.2, 34.05, 5.0]
                },
            }
        ]
    }
    mock_get.return_value = mock_response

    cutoff = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    events = fetch_events_updated_after(cutoff)

    assert len(events) == 1
    assert events[0].id == "us1000test"
    assert events[0].updated_ms == 1700000100000
    assert events[0].mag == 4.2
    assert events[0].longitude == -118.2
    assert events[0].latitude == 34.05
    assert events[0].depth == 5.0

    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert kwargs["params"]["updatedafter"] == "2025-01-01T00:00:00+00:00"


def test_schema_definition():
    assert "earthquake_minute" in schemas
    assert "updated_ms BIGINT" in schemas["earthquake_minute"]