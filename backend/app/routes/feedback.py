from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Feedback
from app.schemas import FeedbackCreate, FeedbackResponse
from app.services.analysis_pipeline import content_fingerprint, run_analysis
from app.services.feedback_mapper import to_feedback_response

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)):
    text = payload.feedback_text.strip()
    if len(text) < 3:
        raise HTTPException(status_code=400, detail="Feedback text must be at least 3 characters")

    fp = content_fingerprint(payload.student_name, payload.topic, text)
    recent_cutoff = datetime.utcnow() - timedelta(seconds=90)
    duplicate = (
        db.query(Feedback)
        .filter(Feedback.content_hash == fp, Feedback.created_at >= recent_cutoff)
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="Duplicate submission detected. Please wait before resubmitting.")

    analysis = run_analysis(text)

    row = Feedback(
        student_name=payload.student_name,
        topic=payload.topic,
        feedback_text=text,
        detected_language=analysis.detected_language,
        sentiment=analysis.sentiment,
        sentiment_confidence=analysis.sentiment_confidence,
        emotion_intensity=analysis.emotion_intensity,
        analysis_status=analysis.analysis_status,
        model_version=analysis.model_version,
        content_hash=fp,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return to_feedback_response(row)


@router.get("/recent", response_model=list[FeedbackResponse])
def recent_feedback(limit: int = 3, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 20))
    rows = db.query(Feedback).order_by(Feedback.created_at.desc()).limit(limit).all()
    return [to_feedback_response(r) for r in rows]
