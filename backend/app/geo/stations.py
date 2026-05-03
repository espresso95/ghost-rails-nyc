from __future__ import annotations

import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel


class CurrentStation(BaseModel):
    id: str
    name: str
    borough: str
    routes: list[str]
    coordinates: tuple[float, float]


class StationCollection(BaseModel):
    stations: list[CurrentStation]


@dataclass(frozen=True)
class NearbyStationResult:
    station: CurrentStation
    distance_m: float


def load_station_collection(path: Path) -> StationCollection:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return StationCollection.model_validate(payload)


@lru_cache(maxsize=8)
def load_cached_station_collection(path_text: str) -> StationCollection:
    return load_station_collection(Path(path_text))


def filter_stations(
    stations: list[CurrentStation],
    route: str | None = None,
    borough: str | None = None,
) -> list[CurrentStation]:
    filtered: list[CurrentStation] = []
    for station in stations:
        if route and route.upper() not in {item.upper() for item in station.routes}:
            continue
        if borough and station.borough.lower() != borough.lower():
            continue
        filtered.append(station)
    return filtered


def nearby_stations(stations: list[CurrentStation], lat: float, lon: float, radius_m: float) -> list[NearbyStationResult]:
    results: list[NearbyStationResult] = []
    for station in stations:
        station_lon, station_lat = station.coordinates
        distance = _haversine_m(lat, lon, station_lat, station_lon)
        if distance <= radius_m:
            results.append(NearbyStationResult(station=station, distance_m=distance))
    results.sort(key=lambda result: result.distance_m)
    return results


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_m = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    return earth_radius_m * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

