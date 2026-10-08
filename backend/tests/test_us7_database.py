import pytest


def _submit(client, text="I really enjoyed this course!", topic="Teacher"):
    return client.post(
        "/api/feedback",
        json={
            "student_name": "Test Student",
            "topic": topic,
            "feedback_text": text,
        },
    )


def test_database_insert_and_fields(client):
    res = _submit(client)
    assert res.status_code == 201
    body = res.json()
    assert body["id"] > 0
    assert body["topic"] == "Teacher"
    assert body["detected_language"] in ("en", "ru", "kk", "unknown")
    assert body["sentiment"] in ("positive", "negative", "neutral", "unknown")
    assert body["analysis_status"] in ("completed", "failed")


def test_recent_endpoint(client):
    _submit(client, "This lesson was boring and difficult.")
    recent = client.get("/api/feedback/recent?limit=5")
    assert recent.status_code == 200
    data = recent.json()
    assert len(data) >= 1


def test_admin_endpoints_protected(client):
    assert client.get("/api/admin/feedback").status_code == 401
    assert client.get("/api/admin/stats").status_code == 401


def test_migration_no_duplicates(admin_client):
    payload = {
        "records": [
            {"id": 1001, "name": "Ali", "topic": "Library", "text": "Good books", "date": "01/03/2026, 10:00:00"},
            {"id": 1001, "name": "Ali", "topic": "Library", "text": "Good books", "date": "01/03/2026, 10:00:00"},
        ]
    }
    first = admin_client.post("/api/admin/migrate", json=payload)
    second = admin_client.post("/api/admin/migrate", json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["imported"] == 1
    assert second.json()["skipped_duplicates"] >= 1


def test_duplicate_submission_blocked(client):
    text = "Duplicate check sample feedback text here."
    first = _submit(client, text=text)
    second = _submit(client, text=text)
    assert first.status_code == 201
    assert second.status_code == 409
