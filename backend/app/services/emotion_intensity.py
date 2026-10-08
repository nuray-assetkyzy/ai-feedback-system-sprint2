"""
US8 — Emotion intensity scoring (1–10).

Documented deterministic lexicon + linguistic feature method.
Sentiment confidence is NOT used as intensity.
Neutral sentiment → no intensity (None).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

INTENSIFIERS = {
    "en": [
        "very", "really", "extremely", "absolutely", "totally", "incredibly",
        "so", "highly", "deeply", "utterly", "completely",
    ],
    "ru": [
        "очень", "крайне", "абсолютно", "совершенно", "чрезвычайно", "невероятно",
        "сильно", "ужасно", "безумно",
    ],
    "kk": [
        "өте", "қатты", "мүлдем", "тамаша", "керемет", "аса", "бірден", "шамадан",
        "қатты", "басым",
    ],
}

STRONG_POSITIVE = {
    "en": ["love", "amazing", "excellent", "fantastic", "wonderful", "best", "awesome"],
    "ru": ["обожаю", "восторг", "прекрасно", "отлично", "лучший", "великолепно"],
    "kk": ["ұнады", "керемет", "тамаша", "керемет", "жақсы", "тамаша"],
}

STRONG_NEGATIVE = {
    "en": ["hate", "worst", "terrible", "awful", "horrible", "disgusting", "useless"],
    "ru": ["ненавижу", "ужасно", "отвратительно", "кошмар", "худший", "скучно"],
    "kk": ["жек көрем", "қиын", "түсініксіз", "нашар", "қорқынышты"],
}

WEAK_MARKERS = {
    "en": ["a little", "somewhat", "bit", "slightly", "okay", "fine", "like"],
    "ru": ["немного", "чуть", "слегка", "нормально", "терпимо"],
    "kk": ["біраз", "сәл", "қалыпты", "жаман емес"],
}

NEGATION = {
    "en": ["not", "never", "no"],
    "ru": ["не", "ни", "никогда"],
    "kk": ["емес", "жоқ", "ешқашан"],
}


@dataclass
class IntensityResult:
    score: int | None
    level: str | None
    explanation: str


def intensity_level(score: int | None) -> str | None:
    if score is None:
        return None
    if score <= 4:
        return "Low"
    if score <= 7:
        return "Moderate"
    return "High"


class EmotionIntensityService:
    def score(self, text: str, sentiment: str, language_code: str) -> IntensityResult:
        if sentiment not in ("positive", "negative"):
            return IntensityResult(
                None,
                None,
                "Emotion intensity is not applicable for neutral or unknown sentiment.",
            )

        cleaned = (text or "").strip()
        if not cleaned:
            return IntensityResult(None, None, "Empty text — intensity not calculated.")

        lang = language_code if language_code in ("en", "ru", "kk") else "en"
        lower = cleaned.lower()
        tokens = re.findall(r"[\w']+", lower, flags=re.UNICODE)

        base = 4.0
        points = 0.0

        intensifier_hits = sum(1 for w in INTENSIFIERS[lang] if w in lower)
        points += min(intensifier_hits * 1.2, 3.0)

        if sentiment == "positive":
            strong_hits = sum(1 for w in STRONG_POSITIVE[lang] if w in lower)
        else:
            strong_hits = sum(1 for w in STRONG_NEGATIVE[lang] if w in lower)
        points += min(strong_hits * 1.5, 4.0)

        weak_hits = sum(1 for w in WEAK_MARKERS[lang] if w in lower)
        points -= min(weak_hits * 1.0, 2.5)

        exclamations = cleaned.count("!")
        points += min(exclamations * 0.6, 2.0)

        if cleaned.isupper() and len(cleaned) > 10:
            points += 1.0

        caps_words = sum(1 for t in re.findall(r"\b[A-ZА-ЯӘҒҚҢӨҰҮІҺ]{3,}\b", cleaned))
        points += min(caps_words * 0.4, 1.5)

        neg_hits = sum(1 for w in NEGATION[lang] if re.search(rf"\b{re.escape(w)}\b", lower))
        if neg_hits and sentiment == "positive":
            points -= 0.8

        raw = base + points
        if sentiment == "negative" and strong_hits >= 2:
            raw += 1.0
        if sentiment == "positive" and "!" in cleaned and strong_hits >= 1:
            raw += 0.5

        score = int(max(1, min(10, round(raw))))
        level = intensity_level(score)
        explanation = (
            f"Score based on emotion words, intensifiers, punctuation, and negation "
            f"({len(tokens)} tokens, language={lang})."
        )
        return IntensityResult(score, level, explanation)
