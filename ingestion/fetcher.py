import requests
from datetime import datetime, timedelta, timezone
from typing import List
from ingestion.models import EarthquakeEvent
import os

# Fetch earthquakes from the past minute
def fetch_last_minute_events() -> List[EarthquakeEvent]:
    end = datetime.now(timezone.utc)
    start = end - timedelta(minutes=1)
    params = {
        "format": "geojson",
        "starttime": start.isoformat(),
        "endtime": end.isoformat(),
    }
    url = os.getenv("USGS_API_URL")
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    events = []
    for f in data.get("features", []):
        props = f.get("properties", {})
        coords = f.get("geometry", {}).get("coordinates", [None, None, None])
        events.append(
            EarthquakeEvent(
                id=f.get("id"),
                time_ms=props.get("time"),
                mag=props.get("mag"),
                place=props.get("place"),
                url=props.get("url"),
                detail=props.get("detail"),
                longitude=coords[0],
                latitude=coords[1],
                depth=coords[2],
            )
        )
    return events