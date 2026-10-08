from app.services.emotion_intensity import EmotionIntensityService


def test_strong_positive_higher_than_weak():
    svc = EmotionIntensityService()
    weak = svc.score("I like this course.", "positive", "en")
    strong = svc.score("I absolutely love this amazing course!", "positive", "en")
    assert weak.score is not None and strong.score is not None
    assert strong.score > weak.score
    assert strong.score >= 8
    assert weak.score <= 4


def test_strong_negative_higher_than_weak():
    svc = EmotionIntensityService()
    weak = svc.score("The lesson is a little boring.", "negative", "en")
    strong = svc.score("This is the worst course ever! I absolutely hate it!", "negative", "en")
    assert weak.score is not None and strong.score is not None
    assert strong.score > weak.score
    assert strong.score >= 8
    assert weak.score <= 4


def test_score_range():
    svc = EmotionIntensityService()
    result = svc.score("Very bad!!!", "negative", "en")
    assert 1 <= result.score <= 10


def test_neutral_not_applicable():
    svc = EmotionIntensityService()
    result = svc.score("The schedule is on Monday.", "neutral", "en")
    assert result.score is None


def test_unknown_sentiment_not_scored():
    svc = EmotionIntensityService()
    result = svc.score("Some text", "unknown", "en")
    assert result.score is None


def test_deterministic():
    svc = EmotionIntensityService()
    a = svc.score("I really love this!", "positive", "en")
    b = svc.score("I really love this!", "positive", "en")
    assert a.score == b.score
