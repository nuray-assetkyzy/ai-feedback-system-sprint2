import hashlib
from dataclasses import dataclass

from app.config import get_settings
from app.services.emotion_intensity import EmotionIntensityService
from app.services.language_detection import get_language_service
from app.services.sentiment_analysis import get_sentiment_service


@dataclass
class AnalysisOutput:
    detected_language: str
    language_name: str
    sentiment: str
    sentiment_confidence: float | None
    emotion_intensity: int | None
    intensity_level: str | None
    intensity_explanation: str
    analysis_status: str
    model_version: str


def content_fingerprint(student_name: str, topic: str, feedback_text: str) -> str:
    payload = f"{student_name}|{topic}|{feedback_text.strip().lower()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def run_analysis(feedback_text: str) -> AnalysisOutput:
    settings = get_settings()
    lang_svc = get_language_service()
    lang = lang_svc.detect(feedback_text)

    sentiment_svc = get_sentiment_service()
    sentiment = sentiment_svc.analyze(feedback_text, lang.code)

    intensity_svc = EmotionIntensityService()
    intensity = intensity_svc.score(feedback_text, sentiment.label, lang.code)

    status = "completed" if sentiment.label != "unknown" else "failed"

    return AnalysisOutput(
        detected_language=lang.code,
        language_name=lang.name,
        sentiment=sentiment.label,
        sentiment_confidence=sentiment.confidence,
        emotion_intensity=intensity.score,
        intensity_level=intensity.level,
        intensity_explanation=intensity.explanation,
        analysis_status=status,
        model_version=settings.model_version,
    )
