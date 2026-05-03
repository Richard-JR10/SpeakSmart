import numpy as np

from app.config import settings
from app.services.hf_phoneme_recognizer import HFPhonemeRecognition, _vocab_from_checkpoint
from app.services.phoneme_assessment import align_phoneme_sequences, assess_pronunciation
from app.services.pronunciation import build_pronunciation_rules, build_target_pronunciation


ARI = "\u3042\u308a"
KITTE = "\u304d\u3063\u3066"
KONBANWA = "\u3053\u3093\u3070\u3093\u306f"


def test_align_phoneme_sequences_handles_matches():
    alignment = align_phoneme_sequences(["a", "r", "i"], ["a", "r", "i"])

    assert [item["operation"] for item in alignment] == ["match", "match", "match"]


def test_align_phoneme_sequences_handles_substitution():
    alignment = align_phoneme_sequences(["a", "r", "i"], ["a", "l", "i"])

    assert alignment[1]["operation"] == "substitution"
    assert alignment[1]["expected_phoneme"] == "r"
    assert alignment[1]["heard_phoneme"] == "l"


def test_align_phoneme_sequences_handles_insertion_and_deletion():
    deletion_alignment = align_phoneme_sequences(["a", "Q", "te"], ["a", "te"])
    insertion_alignment = align_phoneme_sequences(["a", "te"], ["a", "k", "te"])

    assert any(
        item["operation"] == "deletion" and item["expected_phoneme"] == "Q"
        for item in deletion_alignment
    )
    assert any(
        item["operation"] == "insertion" and item["heard_phoneme"] == "k"
        for item in insertion_alignment
    )


def test_align_phoneme_sequences_handles_repeated_phones():
    alignment = align_phoneme_sequences(["a", "a", "i"], ["a", "i"])

    assert [item["operation"] for item in alignment].count("match") == 2
    assert any(
        item["operation"] == "deletion" and item["expected_phoneme"] == "a"
        for item in alignment
    )


def test_align_phoneme_sequences_treats_ctc_n_as_mora_nasal():
    alignment = align_phoneme_sequences(["k", "o", "N"], ["k", "o", "n"])

    assert [item["operation"] for item in alignment] == ["match", "match", "match"]


def test_hf_fallback_vocab_pads_to_checkpoint_head_size():
    stoi, itos = _vocab_from_checkpoint(None, ["a", "i"], target_size=5)

    assert len(stoi) == 5
    assert itos[0] == ""
    assert itos[3] == "__extra_3"
    assert itos[4] == "__extra_4"


def test_hybrid_hf_ctc_exact_match_scores_high(monkeypatch):
    _enable_hybrid(monkeypatch, ["a", "r", "i"])

    result = _assess(ARI, b"student")

    assert result["recognizer"]["ctc_enabled"] is True
    assert result["recognizer"]["fallback_used"] is False
    assert result["phoneme_match_score"] >= 90
    assert all(item["operation"] == "match" for item in result["phonemes"])


def test_hybrid_hf_ctc_marks_substitution(monkeypatch):
    _enable_hybrid(monkeypatch, ["a", "l", "i"])

    result = _assess(ARI, b"student")

    r_phone = next(item for item in result["phonemes"] if item["expected_phoneme"] == "r")
    assert r_phone["operation"] == "substitution"
    assert r_phone["heard_phoneme"] == "l"
    assert r_phone["issue_type"] == "r_flap_issue"
    assert result["feedback"]


def test_hybrid_hf_ctc_marks_missing_small_tsu(monkeypatch):
    _enable_hybrid(monkeypatch, ["k", "i", "t", "e"])

    result = _assess(KITTE, b"student")

    small_tsu = next(item for item in result["phonemes"] if item["expected_phoneme"] == "Q")
    assert small_tsu["operation"] == "deletion"
    assert small_tsu["issue_type"] == "geminate_issue"
    assert any(item["issue_type"] == "geminate_pause" for item in result["feedback"])


def test_hybrid_hf_ctc_keeps_inserted_sound_detail(monkeypatch):
    _enable_hybrid(monkeypatch, ["a", "r", "x", "i"])

    result = _assess(ARI, b"student")

    insertion = next(item for item in result["phonemes"] if item["operation"] == "insertion")
    assert insertion["expected_phoneme"] is None
    assert insertion["heard_phoneme"] == "x"
    assert result["recognizer"]["recognized_phonemes"] == ["a", "r", "x", "i"]


def test_hybrid_hf_ctc_failure_falls_back_to_reference_alignment(monkeypatch):
    monkeypatch.setattr(settings, "PHONEME_ASSESSMENT_PROVIDER", "hybrid_hf_ctc")
    monkeypatch.setattr(settings, "PHONEME_CTC_FALLBACK_ENABLED", True)

    def fail_recognizer(_audio_bytes: bytes):
        raise RuntimeError("model unavailable")

    monkeypatch.setattr(
        "app.services.hf_phoneme_recognizer.recognize_pronunciation_audio",
        fail_recognizer,
    )

    result = _assess(ARI, b"student")

    assert result["recognizer"]["provider"] == "hybrid_hf_ctc"
    assert result["recognizer"]["ctc_enabled"] is False
    assert result["recognizer"]["fallback_used"] is True
    assert "unavailable" in result["recognizer"]["warning"].lower()


def test_hybrid_hf_ctc_does_not_over_penalize_konbanwa_particle_glide(monkeypatch):
    _enable_hybrid(monkeypatch, ["k", "o", "n", "b", "a", "n", "a"])

    result = _assess(KONBANWA, b"student")

    assert result["phoneme_match_score"] >= 88
    assert not any(item["issue_type"] == "mora_nasal" for item in result["feedback"])
    assert not any(item["issue_type"] == "particle_pronunciation" for item in result["feedback"])


def test_hybrid_hf_ctc_still_flags_literal_ha_for_particle_wa(monkeypatch):
    _enable_hybrid(monkeypatch, ["k", "o", "n", "b", "a", "n", "h", "a"])

    result = _assess(KONBANWA, b"student")

    particle_feedback = [
        item for item in result["feedback"] if item["issue_type"] == "particle_pronunciation"
    ]
    assert particle_feedback


def _enable_hybrid(monkeypatch, phonemes: list[str]) -> None:
    monkeypatch.setattr(settings, "PHONEME_ASSESSMENT_PROVIDER", "hybrid_hf_ctc")
    monkeypatch.setattr(settings, "PHONEME_CTC_FALLBACK_ENABLED", True)

    def fake_recognizer(_audio_bytes: bytes):
        return HFPhonemeRecognition(
            recognized_kana="",
            recognized_phonemes=phonemes,
            raw_phonemes=phonemes,
            confidence=0.94,
            token_confidences=[
                {"position": index, "token": token, "confidence": 0.94}
                for index, token in enumerate(phonemes)
            ],
            model_id="mock-hf-ctc",
            device="cpu",
            elapsed_ms=1.0,
        )

    monkeypatch.setattr(
        "app.services.hf_phoneme_recognizer.recognize_pronunciation_audio",
        fake_recognizer,
    )


def _assess(text: str, audio_bytes: bytes):
    target = build_target_pronunciation(text)
    rules = build_pronunciation_rules(text, target)
    features = _features()
    return assess_pronunciation(
        student_audio=audio_bytes,
        student_features=features,
        reference_features=features,
        target_pronunciation=target,
        pronunciation_rules=rules,
        overall_acoustic_score=96.0,
    )


def _features():
    mfcc = np.array(
        [np.linspace(index, index + 1.0, 32) for index in range(13)],
        dtype=np.float32,
    )
    waveform = np.linspace(-0.25, 0.25, 640, dtype=np.float32)
    return {
        "mfcc": mfcc,
        "duration": 1.0,
        "waveform": waveform,
        "sample_rate": 16000,
        "voiced_ratio": 0.9,
    }
