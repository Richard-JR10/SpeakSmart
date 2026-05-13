import numpy as np

from app.services.phoneme_assessment import align_phoneme_sequences, assess_pronunciation
from app.services.pronunciation import build_pronunciation_rules, build_target_pronunciation


ARI = "あり"
KITTE = "きって"
KONBANWA = "こんばんは"


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


def test_dtw_assess_pronunciation_returns_expected_shape():
    target = build_target_pronunciation(ARI)
    rules = build_pronunciation_rules(ARI, target)
    features = _features()
    result = assess_pronunciation(
        student_audio=b"student",
        student_features=features,
        reference_features=features,
        target_pronunciation=target,
        pronunciation_rules=rules,
        overall_acoustic_score=96.0,
    )

    assert "phoneme_match_score" in result
    assert "mora_timing_score" in result
    assert "phonemes" in result
    assert "morae" in result
    assert result["recognizer"]["provider"] == "reference_aligned_phoneme_dtw"


def test_dtw_assess_pronunciation_perfect_match_scores_high():
    target = build_target_pronunciation(ARI)
    rules = build_pronunciation_rules(ARI, target)
    features = _features()
    result = assess_pronunciation(
        student_audio=b"student",
        student_features=features,
        reference_features=features,
        target_pronunciation=target,
        pronunciation_rules=rules,
        overall_acoustic_score=96.0,
    )

    assert result["phoneme_match_score"] >= 85


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
