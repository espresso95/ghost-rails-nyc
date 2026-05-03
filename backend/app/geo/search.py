from __future__ import annotations

import math
from dataclasses import dataclass

from app.geo.features import RailFeature
from app.rag.index import tokenize


@dataclass(frozen=True)
class FeatureSearchResult:
    feature: RailFeature
    score: float


@dataclass(frozen=True)
class NearbyFeatureResult:
    feature: RailFeature
    distance_m: float


def filter_features(
    features: list[RailFeature],
    feature_type: str | None = None,
    borough: str | None = None,
    status: str | None = None,
    bbox: str | None = None,
) -> list[RailFeature]:
    bounds = _parse_bbox(bbox) if bbox else None
    filtered: list[RailFeature] = []

    for feature in features:
        properties = feature.properties
        if feature_type and properties.feature_type != feature_type:
            continue
        if borough and properties.borough.lower() != borough.lower():
            continue
        if status and status.lower() not in properties.status.lower():
            continue
        if bounds and not _geometry_intersects_bbox(feature, bounds):
            continue
        filtered.append(feature)

    return filtered


def search_features(features: list[RailFeature], query: str, limit: int = 10) -> list[FeatureSearchResult]:
    query_terms = tokenize(query)
    if not query_terms:
        return []

    results: list[FeatureSearchResult] = []
    for feature in features:
        haystack = _feature_search_text(feature)
        haystack_terms = set(tokenize(haystack))
        score = 0.0
        for term in query_terms:
            if term in haystack_terms:
                score += 1.0
            if term in feature.properties.name.lower():
                score += 2.0
        if query.lower() in haystack.lower():
            score += 3.0
        if score > 0:
            results.append(FeatureSearchResult(feature=feature, score=score))

    results.sort(key=lambda result: (result.score, result.feature.properties.name), reverse=True)
    return results[:limit]


def nearby_features(features: list[RailFeature], lat: float, lon: float, radius_m: float) -> list[NearbyFeatureResult]:
    results: list[NearbyFeatureResult] = []
    for feature in features:
        distance = _distance_to_feature_m(feature, lat=lat, lon=lon)
        if distance <= radius_m:
            results.append(NearbyFeatureResult(feature=feature, distance_m=distance))

    results.sort(key=lambda result: result.distance_m)
    return results


def _feature_search_text(feature: RailFeature) -> str:
    properties = feature.properties
    values = [
        properties.id,
        properties.name,
        properties.feature_type,
        properties.borough,
        properties.status,
        properties.summary,
        " ".join(properties.nearby_active_routes),
        " ".join(properties.nearby_active_stations),
    ]
    return " ".join(values)


def _parse_bbox(value: str) -> tuple[float, float, float, float]:
    parts = value.split(",")
    if len(parts) != 4:
        raise ValueError("bbox must be min_lon,min_lat,max_lon,max_lat")
    try:
        min_lon, min_lat, max_lon, max_lat = [float(part) for part in parts]
    except ValueError as error:
        raise ValueError("bbox must contain numeric coordinates") from error
    if min_lon > max_lon or min_lat > max_lat:
        raise ValueError("bbox minimums must be less than maximums")
    return min_lon, min_lat, max_lon, max_lat


def _geometry_intersects_bbox(feature: RailFeature, bbox: tuple[float, float, float, float]) -> bool:
    min_lon, min_lat, max_lon, max_lat = bbox
    for lon, lat in _feature_points(feature):
        if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
            return True
    return False


def _distance_to_feature_m(feature: RailFeature, lat: float, lon: float) -> float:
    distances = [_haversine_m(lat, lon, point_lat, point_lon) for point_lon, point_lat in _feature_points(feature)]
    return min(distances) if distances else math.inf


def _feature_points(feature: RailFeature) -> list[tuple[float, float]]:
    coordinates = feature.geometry.coordinates
    if feature.geometry.type == "Point":
        lon, lat = coordinates
        return [(float(lon), float(lat))]
    return [(float(point[0]), float(point[1])) for point in coordinates]


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_m = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return earth_radius_m * c

