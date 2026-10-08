# QA Tests (Sprint 2)

## Run commands (PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -v
```

## Test categories

| File | User story | Type |
|------|------------|------|
| `test_us5_sentiment.py` | US5 | Integration (real model) + API validation |
| `test_us6_language.py` | US6 | Integration (Lingua) |
| `test_us7_database.py` | US7 | Integration (API + SQLite in-memory) |
| `test_us8_intensity.py` | US8 | Unit (deterministic scorer) |

Skip slow NLP integration tests:

```powershell
$env:RUN_NLP_INTEGRATION="0"
pytest -v
```

## Expected coverage

- US5: 6 multilingual sentiment examples, empty input, invalid API payload
- US6: en/ru/kk detection, short/empty/unsupported handling
- US7: insert, recent list, admin auth guard, migration dedupe, duplicate submit guard
- US8: strong vs weak positive/negative, range 1–10, neutral N/A, determinism

Record actual pytest output in your defense slides after running locally.
