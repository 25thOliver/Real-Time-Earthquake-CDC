import requests
from datetime import datetime, timedelta, timezone
from typing import List
from models import EarthquakeEvent
import os


def fetch_events_updated_after(updated_after: datetime) -> List[EarthquakeEvent]:
    url = os.getenv("USGS_API_URL", "https://earthquake.usgs.gov/fdsnws/event/1/query")
    min_mag = os.getenv("USGS_MIN_MAG")

    if updated_after.tzinfo is None:
        updated_after = updated_after.replace(tzinfo=timezone.utc)

    params = {
        "format": "geojson",
        "updatedafter": updated_after.isoformat(timespec="seconds"),
        "orderby": "time",
    }
    if min_mag:
        params["minmagnitude"] = min_mag

    print(f"Fetching events updated after {updated_after.isoformat()} ...")

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

    features = data.get("features", [])
    if not features:
        print("No new or updated events found since last watermark.")
        return []

    events = []
    for f in features:
        props = f.get("properties", {})
        coords = f.get("geometry", {}).get("coordinates", [None, None, None])
        events.append(
            EarthquakeEvent(
                id=f.get("id"),
                time_ms=props.get("time"),
                updated_ms=props.get("updated"),
                mag=props.get("mag"),
                place=props.get("place"),
                url=props.get("url"),
                detail=props.get("detail"),
                longitude=coords[0] if len(coords) > 0 else None,
                latitude=coords[1] if len(coords) > 1 else None,
                depth=coords[2] if len(coords) > 2 else None,
            )
        )

    print(f"Fetched {len(events)} events (new or revised).")
    return events


def fetch_last_minute_events() -> List[EarthquakeEvent]:
    window_minutes = int(os.getenv("FETCH_WINDOW_MINUTES", "5"))
    start = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
    return fetch_events_updated_after(start)