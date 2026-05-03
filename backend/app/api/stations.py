from __future__ import annotations

from fastapi import APIRouter, Query

from app.config import load_settings
from app.geo.stations import filter_stations, load_cached_station_collection, nearby_stations


router = APIRouter(prefix="/api", tags=["stations"])


@router.get("/stations")
def list_stations(route: str | None = None, borough: str | None = None) -> dict[str, object]:
    settings = load_settings()
    collection = load_cached_station_collection(str(settings.stations_path))
    return {"stations": [station.model_dump() for station in filter_stations(collection.stations, route=route, borough=borough)]}


@router.get("/stations/nearby")
def get_nearby_stations(
    lat: float,
    lon: float,
    radius_m: float = Query(default=1000, gt=0, le=50000),
) -> dict[str, object]:
    settings = load_settings()
    collection = load_cached_station_collection(str(settings.stations_path))
    results = nearby_stations(collection.stations, lat=lat, lon=lon, radius_m=radius_m)
    return {
        "query": {"lat": lat, "lon": lon, "radius_m": radius_m},
        "results": [
            {
                "distance_m": round(result.distance_m, 1),
                "station": result.station.model_dump(),
            }
            for result in results
        ],
    }

