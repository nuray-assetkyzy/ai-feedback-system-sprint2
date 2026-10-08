"""US5 — Multilingual sentiment analysis via XLM-RoBERTa."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from transformers import pipeline

from app.config import get_settings


@dataclass
class SentimentResult:
    label: str  # positive | negative | neutral | unknown
    confidence: float | None
    raw_label: str | None


class SentimentAnalysisService:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id
        self._pipe = pipeline(
            "sentiment-analysis",
            model=model_id,
            tokenizer=model_id,
            truncation=True,
            max_length=512,
        )

    @staticmethod
    def _normalize_label(raw: str) -> str:
        key = raw.lower().strip()
        if key in ("positive", "pos", "label_2"):
            return "positive"
        if key in ("negative", "neg", "label_0"):
            return "negative"
        if key in ("neutral", "label_1"):
            return "neutral"
        if "positive" in key:
            return "positive"
        if "negative" in key:
            return "negative"
        if "neutral" in key:
            return "neutral"
        return "unknown"

    def analyze(self, text: str, language_code: str) -> SentimentResult:
        cleaned = (text or "").strip()
        if len(cleaned) < 3:
            return SentimentResult("unknown", None, None)

        try:
            outputs = self._pipe(cleaned)
            if not outputs:
                return SentimentResult("unknown", None, None)
            top = outputs[0]
            raw_label = str(top.get("label", ""))
            score = float(top.get("score", 0.0))
            label = self._normalize_label(raw_label)
            if label == "unknown":
                return SentimentResult("unknown", score, raw_label)
            return SentimentResult(label, score, raw_label)
        except Exception:
            return SentimentResult("unknown", None, None)


@lru_cache
def get_sentiment_service() -> SentimentAnalysisService:
    settings = get_settings()
    return SentimentAnalysisService(settings.sentiment_model_id)
