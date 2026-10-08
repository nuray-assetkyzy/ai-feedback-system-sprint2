# Sprint 2 Implementation Summary

## User stories delivered

| ID | Story | Implementation |
|----|--------|----------------|
| US5 | Sentiment analysis | `sentiment_analysis.py` + XLM-RoBERTa pipeline |
| US6 | Language detection | `language_detection.py` + Lingua (en/ru/kk) |
| US7 | Database persistence | SQLite + SQLAlchemy `feedbacks` table, REST API |
| US8 | Emotion intensity | `emotion_intensity.py` lexicon/feature scorer |

## Architecture

- **Frontend:** Existing `index.html`, `admin.html`, `style.css`, extended `script.js`, new `api.js`
- **Backend:** FastAPI (`backend/app/main.py`) serves API and static Sprint 1/2 UI on one port
- **Auth:** Bcrypt password hash in SQLite; HttpOnly session cookie
- **Migration:** `POST /api/admin/migrate` imports Sprint 1 `localStorage` records (no delete until flag set)

## Database (`feedbacks`)

Fields: `id`, `legacy_id`, `student_name`, `topic`, `feedback_text`, `detected_language`, `sentiment`, `sentiment_confidence`, `emotion_intensity`, `created_at`, `analysis_status`, `model_version`, `content_hash`

## API endpoints

- `GET /api/health`
- `POST /api/feedback`
- `GET /api/feedback/recent`
- `POST /api/admin/login` / `logout` / `session`
- `GET /api/admin/feedback` (filters: topic, sentiment, language)
- `GET /api/admin/stats`
- `POST /api/admin/migrate`

## Defense demo flow (10 steps)

1. Start backend: `uvicorn app.main:app --reload` from `backend/`
2. Open `http://127.0.0.1:8000/index.html`
3. Submit English feedback → show language, sentiment badge, intensity bar
4. Confirm "Saved to database" message
5. Submit Russian example from QA sheet
6. Submit Kazakh example with `ә`, `қ`, etc.
7. Scroll to Recent Feedbacks (from DB)
8. Open Admin → login (credentials in `.env`, default admin/1234 for local dev)
9. Show stats (positive/negative/neutral, avg intensity)
10. Filter by language/sentiment; mention SQLite file `backend/feedback.db`

## Presentation snippets

- **US5:** "We classify feedback with a multilingual transformer; labels are positive, negative, or neutral with a model confidence score."
- **US6:** "Lingua detects en/ru/kk before sentiment so each text is routed correctly; uncertain text returns Unknown."
- **US7:** "All submissions persist in SQLite; admin dashboard reads live aggregates, not localStorage."
- **US8:** "Intensity is a separate 1–10 lexical score for emotional strength; neutral feedback has no intensity."
