from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import create_session_token, require_admin
from app.models import AdminUser, Feedback
from app.schemas import (
    AdminLoginRequest,
    AdminStatsResponse,
    FeedbackResponse,
    MigrateRequest,
    MigrateResponse,
)
from app.services.authentication import verify_password
from app.services.feedback_mapper import to_feedback_response

router = APIRouter(prefix="/api/admin", tags=["admin"])
settings = get_settings()


@router.post("/login")
def admin_login(payload: AdminLoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(AdminUser).filter(AdminUser.username == payload.username.strip()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Wrong username or password")

    token = create_session_token(user.username)
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=settings.session_max_age_seconds,
        path="/",
    )
    return {"ok": True, "username": user.username}


@router.post("/logout")
def admin_logout(response: Response, _: str = Depends(require_admin)):
    response.delete_cookie(settings.session_cookie_name, path="/")
    return {"ok": True}


@router.get("/session")
def admin_session(username: str = Depends(require_admin)):
    return {"authenticated": True, "username": username}


@router.get("/feedback", response_model=list[FeedbackResponse])
def list_feedback(
    topic: str | None = None,
    sentiment: str | None = None,
    language: str | None = None,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
):
    q = db.query(Feedback).order_by(Feedback.created_at.desc())
    if topic:
        q = q.filter(Feedback.topic == topic)
    if sentiment:
        q = q.filter(Feedback.sentiment == sentiment)
    if language:
        q = q.filter(Feedback.detected_language == language)
    rows = q.all()
    return [to_feedback_response(r) for r in rows]


@router.get("/stats", response_model=AdminStatsResponse)
def admin_stats(db: Session = Depends(get_db), _: str = Depends(require_admin)):
    total = db.query(func.count(Feedback.id)).scalar() or 0
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today = db.query(func.count(Feedback.id)).filter(Feedback.created_at >= today_start).scalar() or 0
    positive = db.query(func.count(Feedback.id)).filter(Feedback.sentiment == "positive").scalar() or 0
    negative = db.query(func.count(Feedback.id)).filter(Feedback.sentiment == "negative").scalar() or 0
    neutral = db.query(func.count(Feedback.id)).filter(Feedback.sentiment == "neutral").scalar() or 0
    unknown_sentiment = db.query(func.count(Feedback.id)).filter(Feedback.sentiment == "unknown").scalar() or 0

    avg_intensity = db.query(func.avg(Feedback.emotion_intensity)).filter(
        Feedback.emotion_intensity.isnot(None)
    ).scalar()

    by_topic_rows = db.query(Feedback.topic, func.count(Feedback.id)).group_by(Feedback.topic).all()
    by_lang_rows = db.query(Feedback.detected_language, func.count(Feedback.id)).group_by(
        Feedback.detected_language
    ).all()

    return AdminStatsResponse(
        total=total,
        today=today,
        positive=positive,
        negative=negative,
        neutral=neutral,
        unknown_sentiment=unknown_sentiment,
        average_emotion_intensity=float(avg_intensity) if avg_intensity is not None else None,
        by_topic={t: c for t, c in by_topic_rows},
        by_language={lang: c for lang, c in by_lang_rows},
    )


@router.post("/migrate", response_model=MigrateResponse)
def migrate_local_storage(payload: MigrateRequest, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    imported = 0
    skipped = 0
    seen_legacy: set[int] = set()
    for item in payload.records:
        if not item.topic or not item.text:
            skipped += 1
            continue
        if item.id is not None:
            if item.id in seen_legacy:
                skipped += 1
                continue
            exists = db.query(Feedback).filter(Feedback.legacy_id == item.id).first()
            if exists:
                skipped += 1
                continue
            seen_legacy.add(item.id)

        created_at = datetime.utcnow()
        if item.date:
            for fmt in ("%d/%m/%Y, %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
                try:
                    created_at = datetime.strptime(item.date.strip(), fmt)
                    break
                except ValueError:
                    continue

        row = Feedback(
            legacy_id=item.id,
            student_name=(item.name or "").strip() or None,
            topic=item.topic.strip(),
            feedback_text=item.text.strip(),
            detected_language="unknown",
            sentiment="unknown",
            sentiment_confidence=None,
            emotion_intensity=None,
            created_at=created_at,
            analysis_status="completed",
            model_version="legacy-localStorage",
        )
        db.add(row)
        imported += 1

    db.commit()
    return MigrateResponse(
        imported=imported,
        skipped_duplicates=skipped,
        total_received=len(payload.records),
    )
