import numpy as np

from app.services.pronunciation import (
    build_pronunciation_rules,
    build_target_pronunciation,
)
from app.services.scoring import build_assessment_confidence, score_attempt


KONNICHIWA = "\u3053\u3093\u306b\u3061\u306f"
ARIGATOU_GOZAIMASU = (
    "\u3042\u308a\u304c\u3068\u3046"
    "\u3054\u3056\u3044\u307e\u3059"
)
ARI = "\u3042\u308a"
KITTE = "\u304d\u3063\u3066"


def test_build_target_pronunciation_uses_spoken_particle_romaji():
    target = build_target_pronunciation(KONNICHIWA)

    assert target["kana"] == KONNICHIWA
    assert target["chunks"][-1]["kana"] == "\u306f"
    assert target["chunks"][-1]["romaji"] == "wa"
    assert target["morae"][-1]["romaji"] == "wa"
    assert target["phonemes"]


def test_build_target_pronunciation_marks_small_tsu_phoneme():
    target = build_target_pronunciation(KITTE)

    assert any(phone["symbol"] == "Q" for phone in target["phonemes"])
    assert any(mora["issue_type"] == "geminate_pause" for mora in target["morae"])


def test_build_target_pronunciation_marks_japanese_long_vowel():
    target = build_target_pronunciation(ARIGATOU_GOZAIMASU)

    assert any(phone["issue_type"] == "long_vowel" for phone in target["phonemes"])
    assert any(mora["issue_type"] == "long_vowel" for mora in target["morae"])


def test_build_pronunciation_rules_marks_final_su_for_devoicing_guidance():
    target = build_target_pronunciation(ARIGATOU_GOZAIMASU)

    rules = build_pronunciation_rules(ARIGATOU_GOZAIMASU, target)

    assert rules[-1].issue_type == "devoicing"
    assert "soft" in rules[-1].expected_note.lower()


def test_score_attempt_returns_phoneme_feedback_for_weak_sound(monkeypatch):
    reference_mfcc = np.array(
        [np.linspace(index, index + 1.0, 12) for index in range(12)],
        dtype=np.float32,
    )
    student_mfcc = reference_mfcc.copy()
    student_mfcc[:, 6:] = np.array(
        [np.linspace(12 - index, -12 - index, 6) for index in range(12)],
        dtype=np.float32,
    )

    reference_waveform = np.linspace(-0.25, 0.25, 240, dtype=np.float32)
    student_waveform = reference_waveform.copy()

    def fake_extract_features(audio_bytes: bytes):
        if audio_bytes == b"student":
            return {
                "mfcc": student_mfcc,
                "duration": 1.0,
                "waveform": student_waveform,
                "sample_rate": 16000,
            }

        return {
            "mfcc": reference_mfcc,
            "duration": 1.0,
            "waveform": reference_waveform,
            "sample_rate": 16000,
        }

    monkeypatch.setattr("app.services.scoring.extract_features", fake_extract_features)

    result = score_attempt(
        b"student",
        b"reference",
        target_text=ARI,
        target_pronunciation=build_target_pronunciation(ARI),
    )

    assert result["accuracy_score"] < 90
    assert result["pronunciation_feedback"]
    assert result["pronunciation_feedback"][0]["chunk_index"] == 1
    assert result["pronunciation_feedback"][0]["issue_type"] == "r_sound"
    assert result["pronunciation_feedback"][0]["expected_phoneme"] == "r"
    assert result["pronunciation_feedback"][0]["sound_to_improve"]
    assert result["pronunciation_feedback"][0]["what_happened"]
    assert result["pronunciation_feedback"][0]["how_to_fix"]
    assert result["pronunciation_feedback"][0]["try_slowly"]
    assert result["phoneme_error_map"]["phonemes"]
    assert result["phoneme_error_map"]["morae"]
    assert result["phoneme_error_map"]["assessment_confidence"]["level"] == "low"
    assert result["phoneme_error_map"]["calibration"]["teacher_ground_truth_used"] is False
    assert result["target_pronunciation"]["phonemes"]


def test_assessment_confidence_is_high_when_recognizer_and_scores_agree():
    confidence = build_assessment_confidence(
        phoneme_match_score=94.0,
        mora_timing_score=91.0,
        consonant_score=92.0,
        vowel_score=96.0,
        fluency_score=93.0,
        recognizer={
            "ctc_enabled": True,
            "fallback_used": False,
            "confidence": 0.91,
            "warning": None,
        },
    )

    assert confidence["level"] == "high"


def test_assessment_confidence_is_low_when_hf_fallback_is_used():
    confidence = build_assessment_confidence(
        phoneme_match_score=82.0,
        mora_timing_score=81.0,
        consonant_score=84.0,
        vowel_score=83.0,
        fluency_score=80.0,
        recognizer={
            "ctc_enabled": False,
            "fallback_used": True,
            "warning": "HF CTC recognizer was unavailable.",
        },
    )

    assert confidence["level"] == "low"
    assert "clearer audio" in confidence["guidance"].lower()
