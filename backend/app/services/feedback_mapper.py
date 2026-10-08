from app.models import Feedback
from app.schemas import FeedbackResponse
from app.services.emotion_intensity import intensity_level

LANGUAGE_NAMES = {
    "en": "English",
    "ru": "Russian",
    "kk": "Kazakh",
    "unknown": "Unknown",
}


def to_feedback_response(row: Feedback) -> FeedbackResponse:
    lang_name = LANGUAGE_NAMES.get(row.detected_language, "Unknown")
    level = intensity_level(row.emotion_intensity) if row.emotion_intensity else None
    return FeedbackResponse(
        id=row.id,
        student_name=row.student_name,
        topic=row.topic,
        feedback_text=row.feedback_text,
        detected_language=row.detected_language,
        language_name=lang_name,
        sentiment=row.sentiment,
        sentiment_confidence=row.sentiment_confidence,
        emotion_intensity=row.emotion_intensity,
        intensity_level=level,
        created_at=row.created_at,
        analysis_status=row.analysis_status,
        model_version=row.model_version,
    )
