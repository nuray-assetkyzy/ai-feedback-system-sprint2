# AI Feedback System (INF 451)

Sprint 1 static website extended in **Sprint 2** with FastAPI, SQLite, multilingual NLP, and automated tests.

## Features

- Student feedback form (unchanged topics and layout)
- **US6** Language detection (English, Russian, Kazakh)
- **US5** Sentiment analysis (positive / negative / neutral)
- **US8** Emotion intensity (1–10 with Low / Moderate / High)
- **US7** SQLite persistence + admin statistics
- Secure admin login (backend bcrypt + HttpOnly cookie)
- Optional import of Sprint 1 `localStorage` data after admin login

## Requirements

- Windows 10/11
- **Python 3.10+** (3.11 recommended) from [python.org](https://www.python.org/downloads/) — check **“Add python.exe to PATH”** during setup  
  (The Microsoft Store stub alone is not enough if `python --version` fails.)
- ~4 GB free RAM for sentiment model
- ~2 GB disk space for Python packages + model download (first run)

See [docs/NLP-MODELS.md](docs/NLP-MODELS.md) for model sizes and limitations.

## Quick start (PowerShell)

```powershell
cd path\to\ai-feedback-system-main\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env: set SECRET_KEY and ADMIN_PASSWORD for local use
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open in browser:

- Student page: http://127.0.0.1:8000/index.html
- Admin page: http://127.0.0.1:8000/admin.html
- API health: http://127.0.0.1:8000/api/health

**Important:** Use the URL above (through Uvicorn). Opening `index.html` directly from the filesystem will not reach the API.

### Default admin (local dev only)

Configure in `backend/.env`:

```
ADMIN_USERNAME=admin
ADMIN_PASSWORD=1234
```

Change the password before any shared demo. Passwords are not stored in JavaScript.

### Stop / restart

- Stop server: `Ctrl+C` in the terminal
- Restart: run the `uvicorn` command again
- Database file: `backend/feedback.db` (persists after restart)

## Tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest -v
```

Details: [docs/QA-TESTS.md](docs/QA-TESTS.md)

## Sprint 2 documentation

- [docs/SPRINT2.md](docs/SPRINT2.md) — defense summary
- [docs/NLP-MODELS.md](docs/NLP-MODELS.md) — models and intensity method

## Repository

https://github.com/abdulgazieva1310-netizen/ai-feedback-system
