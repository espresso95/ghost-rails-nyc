from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.config import load_settings
from app.geo.features import FeatureCollection, RailFeature, get_feature_by_id, load_cached_feature_collection
from app.geo.search import filter_features, nearby_features, search_features


router = APIRouter(prefix="/api", tags=["features"])


@router.get("/features")
def list_features(
    feature_type: str | None = None,
    borough: str | None = None,
    status: str | None = None,
    bbox: str | None = Query(default=None, description="min_lon,min_lat,max_lon,max_lat"),
) -> dict[str, object]:
    collection = _load_collection()
    features = filter_features(collection.features, feature_type=feature_type, borough=borough, status=status, bbox=bbox)
    return FeatureCollection(type="FeatureCollection", features=features).model_dump()


@router.get("/features/nearby")
def get_nearby_features(
    lat: float,
    lon: float,
    radius_m: float = Query(default=1000, gt=0, le=50000),
) -> dict[str, object]:
    collection = _load_collection()
    results = nearby_features(collection.features, lat=lat, lon=lon, radius_m=radius_m)
    return {
        "query": {"lat": lat, "lon": lon, "radius_m": radius_m},
        "results": [
            {
                "distance_m": round(result.distance_m, 1),
                "feature": result.feature.model_dump(),
            }
            for result in results
        ],
    }


@router.get("/features/{feature_id}")
def get_feature(feature_id: str) -> dict[str, object]:
    collection = _load_collection()
    feature = get_feature_by_id(collection, feature_id)
    if feature is None:
        raise HTTPException(status_code=404, detail=f"Feature not found: {feature_id}")
    return feature.model_dump()


@router.get("/search")
def search(q: str = Query(min_length=1), limit: int = Query(default=10, ge=1, le=50)) -> dict[str, object]:
    collection = _load_collection()
    results = search_features(collection.features, q, limit=limit)
    return {
        "query": q,
        "results": [
            {
                "score": round(result.score, 3),
                "feature": result.feature.model_dump(),
            }
            for result in results
        ],
    }


def _load_collection() -> FeatureCollection:
    settings = load_settings()
    return load_cached_feature_collection(str(settings.features_path))

