import pytest

from app.services.language_detection import LanguageDetectionService
from tests.conftest import integration_enabled


@pytest.mark.skipif(not integration_enabled(), reason="Set RUN_NLP_INTEGRATION=1 to run model tests")
@pytest.mark.integration
class TestLanguageDetectionIntegration:
    @pytest.fixture(scope="class")
    def service(self):
        return LanguageDetectionService()

    @pytest.mark.parametrize(
        "text,expected_code",
        [
            ("The teacher explains everything clearly.", "en"),
            ("Преподаватель очень хорошо объясняет материал.", "ru"),
            ("Мұғалім сабақты өте жақсы түсіндіреді.", "kk"),
        ],
    )
    def test_supported_languages(self, service, text, expected_code):
        result = service.detect(text)
        assert result.code == expected_code

    def test_short_text_unknown(self, service):
        assert service.detect("hi").code == "unknown"

    def test_empty_unknown(self, service):
        assert service.detect("").code == "unknown"

    def test_unsupported_language_safe(self, service):
        result = service.detect("Bonjour le monde, ceci est en français avec plusieurs mots.")
        assert result.code in ("unknown", "en", "ru", "kk")
