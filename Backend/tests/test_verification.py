from app.services.verification import (
    VERIFICATION_ACCEPTED,
    VERIFICATION_NO_CLEAR_SPEECH,
    VERIFICATION_RETRY,
    VERIFICATION_WRONG_PHRASE,
    classify_verification_result,
    format_recognized_text_for_feedback,
    normalize_phrase_text,
    sanitize_transcript,
    select_verification_candidates,
)


KONNICHIWA = "\u3053\u3093\u306b\u3061\u306f"
KONBANWA = "\u3053\u3093\u3070\u3093\u306f"
ARIGATOU = "\u3042\u308a\u304c\u3068\u3046"
KATAKANA_KONBANWA = "\u30b3\u30f3\u30d0\u30f3\u306f"
TASUKETE = "\u30bf\u30b9\u30b1\u30c6"


def test_normalize_phrase_text_removes_spacing_and_punctuation():
    assert normalize_phrase_text(f"  {KONNICHIWA}\u3002 ") == KONNICHIWA


def test_normalize_phrase_text_matches_katakana_and_hiragana():
    assert normalize_phrase_text(KATAKANA_KONBANWA) == normalize_phrase_text(KONBANWA)


def test_format_recognized_text_for_feedback_returns_romaji():
    assert format_recognized_text_for_feedback(TASUKETE) == "Tasukete"


def test_select_verification_candidates_keeps_target_first():
    candidates = select_verification_candidates(
        target_phrase_id="target",
        target_text=KONNICHIWA,
        candidates=[
            ("other-1", KONBANWA),
            ("target", KONNICHIWA),
            ("other-2", f"{ARIGATOU}\u3054\u3056\u3044\u307e\u3059"),
        ],
        max_candidates=2,
    )

    assert candidates[0].phrase_id == "target"
    assert len(candidates) == 2


def test_classify_verification_result_accepts_target_match():
    candidates = select_verification_candidates(
        target_phrase_id="target",
        target_text=KONNICHIWA,
        candidates=[
            ("target", KONNICHIWA),
            ("other", KONBANWA),
        ],
    )

    result = classify_verification_result(
        target_phrase_id="target",
        recognized_text=KONNICHIWA,
        candidates=candidates,
        voiced_ratio=0.8,
    )

    assert result.status == VERIFICATION_ACCEPTED
    assert result.recognized_phrase_id == "target"
    assert result.recognized_text_romaji == "Konnichiwa"


def test_sanitize_transcript_collapses_repeated_candidate_phrase():
    candidates = select_verification_candidates(
        target_phrase_id="target",
        target_text=KONBANWA,
        candidates=[
            ("target", KONBANWA),
            ("other", KONNICHIWA),
        ],
    )

    assert sanitize_transcript(KONNICHIWA * 3, candidates) == KONNICHIWA


def test_classify_verification_result_accepts_katakana_transcript_for_hiragana_target():
    candidates = select_verification_candidates(
        target_phrase_id="target",
        target_text=KONBANWA,
        candidates=[
            ("target", KONBANWA),
            ("other", KONNICHIWA),
        ],
    )

    result = classify_verification_result(
        target_phrase_id="target",
        recognized_text=KATAKANA_KONBANWA,
        candidates=candidates,
        voiced_ratio=0.8,
    )

    assert result.status == VERIFICATION_ACCEPTED
    assert result.recognized_phrase_id == "target"
    assert result.recognized_text_romaji == "Konbanwa"


def test_classify_verification_result_flags_wrong_phrase():
    candidates = select_verification_candidates(
        target_phrase_id="target",
        target_text=KONNICHIWA,
        candidates=[
            ("target", KONNICHIWA),
            ("other", KONBANWA),
        ],
    )

    result = classify_verification_result(
        target_phrase_id="target",
        recognized_text=KONBANWA,
        candidates=candidates,
        voiced_ratio=0.8,
    )

    assert result.status == VERIFICATION_WRONG_PHRASE
    assert result.recognized_phrase_id == "other"


def test_classify_verification_result_uses_no_clear_speech_for_empty_audio():
    candidates = select_verification_candidates(
        target_phrase_id="target",
        target_text=KONNICHIWA,
        candidates=[("target", KONNICHIWA)],
    )

    result = classify_verification_result(
        target_phrase_id="target",
        recognized_text="",
        candidates=candidates,
        voiced_ratio=0.01,
    )

    assert result.status == VERIFICATION_NO_CLEAR_SPEECH


def test_classify_verification_result_retries_on_uncertain_match():
    candidates = select_verification_candidates(
        target_phrase_id="target",
        target_text=KONNICHIWA,
        candidates=[
            ("target", KONNICHIWA),
            ("other", ARIGATOU),
        ],
    )

    result = classify_verification_result(
        target_phrase_id="target",
        recognized_text="\u3053\u3093",
        candidates=candidates,
        voiced_ratio=0.8,
        acceptance_confidence=0.95,
        wrong_phrase_confidence=0.95,
        min_margin=0.5,
    )

    assert result.status == VERIFICATION_RETRY


def test_classify_verification_result_does_not_force_arbitrary_english_into_phrase():
    candidates = select_verification_candidates(
        target_phrase_id="target",
        target_text=KONNICHIWA,
        candidates=[
            ("target", KONNICHIWA),
            ("other", KONBANWA),
        ],
    )

    result = classify_verification_result(
        target_phrase_id="target",
        recognized_text="test",
        candidates=candidates,
        voiced_ratio=0.8,
    )

    assert result.status == VERIFICATION_RETRY
    assert result.recognized_phrase_id is None
    assert result.recognized_text == "test"
