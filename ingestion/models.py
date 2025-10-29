from dataclasses import dataclass
from typing import Optional

@dataclass
class EarthquakeEvent:
    id: str
    time_ms: int
    mag: Optional[float]
    place: Optional[str]
    url: Optional[str]
    detail: Optional[str]
    longitude: Optional[float]
    latitude: Optional[float]
    depth: Optional[float]