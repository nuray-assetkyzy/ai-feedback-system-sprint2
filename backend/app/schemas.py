from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

AnalysisStatus = Literal["processing", "completed", "failed"]
SentimentLabel = Literal["positive", "negative", "neutral", "unknown"]
LanguageCode = Literal["en", "ru", "kk", "unknown"]


class FeedbackCreate(BaseModel):
    student_name: str = Field(..., min_length=1, max_length=255)
    topic: str = Field(..., min_length=1, max_length=64)
    feedback_text: str = Field(..., min_length=3, max_length=5000)
    client_nonce: str | None = Field(default=None, max_length=64)

    @field_validator("student_name", "topic", "feedback_text")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()


class FeedbackResponse(BaseModel):
    id: int
    student_name: str | None
    topic: str
    feedback_text: str
    detected_language: str
    language_name: str
    sentiment: str
    sentiment_confidence: float | None
    emotion_intensity: int | None
    intensity_level: str | None
    created_at: datetime
    analysis_status: str
    model_version: str | None

    model_config = {"from_attributes": True}


class LegacyFeedbackItem(BaseModel):
    id: int | None = None
    name: str | None = None
    topic: str
    text: str
    date: str | None = None


class MigrateRequest(BaseModel):
    records: list[LegacyFeedbackItem] = Field(default_factory=list)


class MigrateResponse(BaseModel):
    imported: int
    skipped_duplicates: int
    total_received: int


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminStatsResponse(BaseModel):
    total: int
    today: int
    positive: int
    negative: int
    neutral: int
    unknown_sentiment: int
    average_emotion_intensity: float | None
    by_topic: dict[str, int]
    by_language: dict[str, int]
