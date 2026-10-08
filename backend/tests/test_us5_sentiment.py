import pytest

from app.services.sentiment_analysis import SentimentAnalysisService
from tests.conftest import integration_enabled

pytestmark_integration = pytest.mark.integration


@pytest.mark.skipif(not integration_enabled(), reason="Set RUN_NLP_INTEGRATION=1 to run model tests")
@pytest.mark.integration
class TestSentimentIntegration:
    @pytest.fixture(scope="class")
    def service(self):
        from app.config import get_settings

        return SentimentAnalysisService(get_settings().sentiment_model_id)

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("I really enjoyed this course!", "positive"),
            ("This teacher explains everything badly.", "negative"),
            ("Мне очень понравился этот урок!", "positive"),
            ("Этот урок был очень скучным.", "negative"),
            ("Бұл сабақ маған өте ұнады!", "positive"),
            ("Сабақ өте қиын және түсініксіз болды.", "negative"),
        ],
    )
    def test_multilingual_sentiment_examples(self, service, text, expected):
        result = service.analyze(text, "en")
        assert result.label == expected

    def test_empty_input(self, service):
        assert service.analyze("", "en").label == "unknown"


def test_invalid_feedback_rejected(client):
    res = client.post(
        "/api/feedback",
        json={"student_name": "A", "topic": "Teacher", "feedback_text": "ok"},
    )
    assert res.status_code == 422
