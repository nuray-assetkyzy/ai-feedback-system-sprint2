"""US6 — Language detection for en, ru, kk using Lingua."""

from __future__ import annotations

from dataclasses import dataclass

from lingua import Language, LanguageDetectorBuilder

SUPPORTED = {
    Language.ENGLISH: ("en", "English"),
    Language.RUSSIAN: ("ru", "Russian"),
    Language.KAZAKH: ("kk", "Kazakh"),
}

KAZAKH_SPECIFIC = set("әғқңөұүіһ")


@dataclass
class LanguageResult:
    code: str
    name: str
    confidence: float | None


class LanguageDetectionService:
    def __init__(self) -> None:
        self._detector = (
            LanguageDetectorBuilder.from_languages(*SUPPORTED.keys())
            .with_minimum_relative_distance(0.15)
            .build()
        )

    @staticmethod
    def _kazakh_script_hint(text: str) -> bool:
        lower = text.lower()
        return any(ch in lower for ch in KAZAKH_SPECIFIC)

    def detect(self, text: str) -> LanguageResult:
        cleaned = (text or "").strip()
        if not cleaned:
            return LanguageResult("unknown", "Unknown", None)
        if len(cleaned) < 3:
            return LanguageResult("unknown", "Unknown", None)

        if self._kazakh_script_hint(cleaned):
            kk_conf = self._detector.compute_language_confidence(cleaned, Language.KAZAKH)
            if kk_conf >= 0.35:
                return LanguageResult("kk", "Kazakh", float(kk_conf))

        detected = self._detector.detect_language_of(cleaned)
        if detected is None:
            return LanguageResult("unknown", "Unknown", None)

        if detected not in SUPPORTED:
            return LanguageResult("unknown", "Unknown", None)

        conf_values = self._detector.compute_language_confidence_values(cleaned)
        confidence = None
        for item in conf_values:
            if item.language == detected:
                confidence = float(item.value)
                break

        code, name = SUPPORTED[detected]
        if confidence is not None and confidence < 0.35:
            return LanguageResult("unknown", "Unknown", confidence)

        return LanguageResult(code, name, confidence)


_language_service: LanguageDetectionService | None = None


def get_language_service() -> LanguageDetectionService:
    global _language_service
    if _language_service is None:
        _language_service = LanguageDetectionService()
    return _language_service
