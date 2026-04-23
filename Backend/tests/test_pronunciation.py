import numpy as np

from app.services.pronunciation import (
    build_pronunciation_rules,
    build_target_pronunciation,
)
from app.services.scoring import score_attempt


KONNICHIWA = "\u3053\u3093\u306b\u3061\u306f"
ARIGATOU_GOZAIMASU = (
    "\u3042\u308a\u304c\u3068\u3046"
    "\u3054\u3056\u3044\u307e\u3059"
)
ARI = "\u3042\u308a"


def test_build_target_pronunciation_uses_spoken_particle_romaji():
    target = build_target_pronunciation(KONNICHIWA)

    assert target["kana"] == KONNICHIWA
    assert target["chunks"][-1]["kana"] == "\u306f"
    assert target["chunks"][-1]["romaji"] == "wa"


def test_build_pronunciation_rules_marks_final_su_for_devoicing_guidance():
    target = build_target_pronunciation(ARIGATOU_GOZAIMASU)

    rules = build_pronunciation_rules(ARIGATOU_GOZAIMASU, target)

    assert rules[-1].issue_type == "devoicing"
    assert "soft" in rules[-1].expected_note.lower()


def test_score_attempt_returns_chunk_level_feedback_for_weak_chunk(monkeypatch):
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
