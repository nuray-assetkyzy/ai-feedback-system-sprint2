# NLP Models & Methods (Sprint 2)

## Language detection (US6)

- **Library:** [Lingua](https://github.com/pemistahl/lingua) (`lingua-language-detector` 2.x)
- **Languages loaded:** English, Russian, Kazakh only (reduces false positives)
- **Download size:** ~1–2 MB (rules/statistics, no large neural download)
- **RAM:** ~50–100 MB during detection
- **Kazakh vs Russian:** Both use Cyrillic; Kazakh-specific letters (`ә`, `ғ`, `қ`, `ң`, `ө`, `ұ`, `ү`, `і`, `һ`) trigger an extra Kazakh confidence check before accepting Russian.
- **Uncertainty:** If confidence &lt; 0.35 or language not in {en, ru, kk}, returns **Unknown**.

## Sentiment analysis (US5)

- **Model:** `cardiffnlp/twitter-xlm-roberta-base-sentiment` (Hugging Face Transformers)
- **Type:** Multilingual XLM-RoBERTa fine-tuned for sentiment (negative / neutral / positive)
- **First-run download:** ~1.1 GB (model weights + tokenizer)
- **RAM:** ~2–4 GB recommended while the model is loaded
- **Languages:** Strong on English and Russian; Kazakh is supported via multilingual pre-training but is **less reliable** than en/ru. Results are never hardcoded.
- **Confidence:** The `score` field is the model's softmax probability for the predicted label — useful for ranking, **not** guaranteed real-world accuracy.

## Emotion intensity (US8)

- **Method:** Deterministic lexicon + linguistic features (`emotion_intensity.py`)
- **Not used:** Sentiment softmax confidence as intensity (explicitly excluded)
- **Features:** Intensifiers (en/ru/kk), strong/weak emotion lemmas, `!` marks, ALL CAPS, negation
- **Scale:** Integer 1–10 → Low (1–4), Moderate (5–7), High (8–10)
- **Neutral policy:** `emotion_intensity = null`, UI shows "Not applicable"
- **Limitation:** Lexicon coverage for Kazakh is smaller than English; scores are approximate but consistent (deterministic).

## Limitations (defense talking points)

1. First server start may take several minutes while the sentiment model downloads.
2. Kazakh sentiment may occasionally be misclassified; language detection is stronger than Kazakh sentiment.
3. Intensity for legacy migrated records without re-analysis remains empty until re-submitted.
4. Laptop GPU is optional; CPU inference works but is slower.
