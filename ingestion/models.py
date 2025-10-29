from dataclasses import dataclass


@dataclass
class EarthquakeEvent:
    id: str
    time_ms: int
    mag: float
    place: str
    url: str
    detail: str
    longitude: float
    latitude: float
    depth: float