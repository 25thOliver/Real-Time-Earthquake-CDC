import requests
from datetime import datetime, timedelta, timezone
from typing import List
from models import EarthquakeEvent
import os


# Fetch earthquake events from the past minute using the USGS API
# Returns an empty list if no events are found
def fetch_last_minute_events() -> List[EarthquakeEvent]:
    # Defaults: fetch a slightly wider window to reduce gaps, rely on PK dedupe
    window_minutes = int(os.getenv("FETCH_WINDOW_MINUTES", "5"))
    end = datetime.now(timezone.utc)
    start = end - timedelta(minutes=window_minutes)
    url = os.getenv("USGS_API_URL", "https://earthquake.usgs.gov/fdsnws/event/1/query")
    min_mag = os.getenv("USGS_MIN_MAG")  # optional

    params = {
        "format": "geojson",
        "starttime": start.isoformat(timespec="seconds"),
        "endtime": end.isoformat(timespec="seconds"),
        "orderby": "time",
    }
    if min_mag:
        params["minmagnitude"] = min_mag

    print(f"Fetching events from {start.isoformat()} to {end.isoformat()} ...")

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

    features = data.get("features", [])
    if not features:
        print("No events in the past minute -- waiting for the next poll.")
        return []
    
    events = []
    for f in features:
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

    print(f"Fetched {len(events)} events.")
    return events


if __name__ == "__main__":
    events = fetch_last_minute_events()
    print(f"Fetched {len(events)} total events.")
    if events:
        for e in events[:3]: 
            print(e.__dict__)
