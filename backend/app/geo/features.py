from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, field_validator


FeatureType = Literal[
    "abandoned_station",
    "closed_platform",
    "unused_provision",
    "former_elevated",
    "disused_corridor",
    "freight_corridor",
    "museum_station",
]

SafetyClassification = Literal[
    "public_view_only",
    "museum_or_official_tour",
    "do_not_access",
    "historical_only",
    "uncertain",
]


class Geometry(BaseModel):
    type: Literal["Point", "LineString"]
    coordinates: list[float] | list[list[float]]

    @field_validator("coordinates")
    @classmethod
    def validate_coordinates(cls, coordinates: list[float] | list[list[float]]) -> list[float] | list[list[float]]:
        if _is_point(coordinates) or _is_line_string(coordinates):
            return coordinates
        raise ValueError("geometry coordinates must be a Point or LineString")


class RailFeatureProperties(BaseModel):
    id: str
    name: str
    feature_type: FeatureType
    borough: str
    status: str
    opened_year: int | None = None
    closed_year: int | None = None
    nearby_active_routes: list[str] = Field(default_factory=list)
    nearby_active_stations: list[str] = Field(default_factory=list)
    visibility: str
    safety_classification: SafetyClassification
    summary: str
    source_ids: list[str]

    @field_validator("source_ids")
    @classmethod
    def require_source_ids(cls, source_ids: list[str]) -> list[str]:
        if not source_ids:
            raise ValueError("source_ids must not be empty")
        return source_ids


class RailFeature(BaseModel):
    type: Literal["Feature"]
    geometry: Geometry
    properties: RailFeatureProperties


class FeatureCollection(BaseModel):
    type: Literal["FeatureCollection"]
    features: list[RailFeature]


def load_feature_collection(path: Path) -> FeatureCollection:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise FileNotFoundError(f"Feature dataset not found: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Feature dataset is not valid JSON: {path}") from error

    try:
        collection = FeatureCollection.model_validate(payload)
    except ValidationError as error:
        raise ValueError(f"Feature dataset failed validation: {path}") from error

    _validate_unique_ids(collection)
    return collection


@lru_cache(maxsize=8)
def load_cached_feature_collection(path_text: str) -> FeatureCollection:
    return load_feature_collection(Path(path_text))


def get_feature_by_id(collection: FeatureCollection, feature_id: str) -> RailFeature | None:
    for feature in collection.features:
        if feature.properties.id == feature_id:
            return feature
    return None


def _validate_unique_ids(collection: FeatureCollection) -> None:
    seen: set[str] = set()
    duplicate_ids: list[str] = []
    for feature in collection.features:
        feature_id = feature.properties.id
        if feature_id in seen:
            duplicate_ids.append(feature_id)
        seen.add(feature_id)
    if duplicate_ids:
        raise ValueError(f"Feature dataset contains duplicate IDs: {', '.join(sorted(duplicate_ids))}")


def _is_point(coordinates: object) -> bool:
    return (
        isinstance(coordinates, list)
        and len(coordinates) == 2
        and all(isinstance(value, int | float) for value in coordinates)
    )


def _is_line_string(coordinates: object) -> bool:
    return (
        isinstance(coordinates, list)
        and len(coordinates) >= 2
        and all(_is_point(point) for point in coordinates)
    )

