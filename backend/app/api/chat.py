from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.config import load_settings
from app.geo.features import load_cached_feature_collection
from app.rag.answer import answer_question


router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    selected_feature_id: str | None = None
    include_sources: bool = True


@router.post("/chat")
def post_chat(request: ChatRequest) -> dict[str, object]:
    settings = load_settings()
    features = load_cached_feature_collection(str(settings.features_path))
    response = answer_question(
        question=request.question,
        selected_feature_id=request.selected_feature_id,
        settings=settings,
        features=features,
        include_sources=request.include_sources,
    )
    return response.as_dict()

