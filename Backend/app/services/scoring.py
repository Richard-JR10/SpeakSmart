from __future__ import annotations

from statistics import mean
from typing import Any

import numpy as np
from scipy.spatial.distance import cdist

from app.services.pronunciation import (
    build_pronunciation_rules,
    build_target_pronunciation,
    summarize_pronunciation_feedback,
)
from app.services.speech import extract_features


def normalize_feature_sequence(seq: np.ndarray) -> np.ndarray:
    """
    Normalize each MFCC coefficient to zero mean and unit variance so the
    comparison is less sensitive to microphone gain and voice timbre.
    """
    mean_value = np.mean(seq, axis=1, keepdims=True)
    std = np.std(seq, axis=1, keepdims=True)
    return (seq - mean_value) / np.maximum(std, 1e-6)


def dtw_distance(seq_a: np.ndarray, seq_b: np.ndarray) -> float:
    """
    Computes the normalized DTW distance between two MFCC sequences.
    """
    if seq_a.size == 0 or seq_b.size == 0:
        return 1.6

    a = normalize_feature_sequence(seq_a).T
    b = normalize_feature_sequence(seq_b).T

    cost_matrix = cdist(a, b, metric="cosine")

    t1, t2 = cost_matrix.shape
    accumulated = np.full((t1, t2), np.inf)
    accumulated[0, 0] = cost_matrix[0, 0]

    for i in range(1, t1):
        accumulated[i, 0] = accumulated[i - 1, 0] + cost_matrix[i, 0]
    for j in range(1, t2):
        accumulated[0, j] = accumulated[0, j - 1] + cost_matrix[0, j]

    for i in range(1, t1):
        for j in range(1, t2):
            accumulated[i, j] = cost_matrix[i, j] + min(
                accumulated[i - 1, j],
                accumulated[i, j - 1],
                accumulated[i - 1, j - 1],
            )

    normalized = accumulated[t1 - 1, t2 - 1] / (t1 + t2)
    return float(normalized)


def dtw_to_score(dtw_dist: float) -> float:
    """
    Converts a raw DTW distance to a 0-100 score.
    """
    if dtw_dist <= 0:
        return 100.0

    thresholds = [
        (0.12, 96.0),
        (0.20, 90.0),
        (0.32, 82.0),
        (0.45, 72.0),
        (0.60, 60.0),
        (0.80, 45.0),
        (1.00, 30.0),
        (1.25, 15.0),
    ]

    previous_dist = 0.0
    previous_score = 100.0
    for threshold_dist, threshold_score in thresholds:
        if dtw_dist <= threshold_dist:
            span = threshold_dist - previous_dist
            if span <= 0:
                return round(threshold_score, 2)
            ratio = (dtw_dist - previous_dist) / span
            interpolated = previous_score + ((threshold_score - previous_score) * ratio)
            return round(interpolated, 2)
        previous_dist = threshold_dist
        previous_score = threshold_score

    if dtw_dist >= 1.6:
        return 0.0

    tail_ratio = (dtw_dist - 1.25) / 0.35
    return round(max(0.0, 15.0 * (1.0 - tail_ratio)), 2)


def score_mora_timing(student_duration: float, reference_duration: float) -> float:
    """
    Scores mora timing accuracy based on duration ratio.
    """
    if reference_duration <= 0:
        return 100.0

    ratio = student_duration / reference_duration
    deviation = abs(1.0 - ratio)

    if deviation <= 0.15:
        return 100.0
    if deviation >= 0.60:
        return 0.0

    score = 100.0 * (1.0 - ((deviation - 0.15) / 0.45))
    return round(max(0.0, min(score, 100.0)), 2)


def score_consonants(student_mfcc: np.ndarray, reference_mfcc: np.ndarray) -> float:
    """
    Scores consonant accuracy using upper MFCC bands (coefficients 6-12).
    """
    upper_student = student_mfcc[6:, :]
    upper_reference = reference_mfcc[6:, :]
    return _safe_slice_score(upper_student, upper_reference)


def score_vowels(student_mfcc: np.ndarray, reference_mfcc: np.ndarray) -> float:
    """
    Scores vowel purity using lower MFCC bands (coefficients 1-5).
    """
    lower_student = student_mfcc[1:6, :]
    lower_reference = reference_mfcc[1:6, :]
    return _safe_slice_score(lower_student, lower_reference)


def build_phoneme_error_map(
    mora_timing_score: float,
    consonant_score: float,
    vowel_score: float,
    dtw_score: float,
) -> dict:
    """
    Builds a compact category summary for the frontend.
    """
    return {
        "mora_timing": {
            "score": mora_timing_score,
            "error": mora_timing_score < 70,
            "label": "Mora Timing",
        },
        "consonants": {
            "score": consonant_score,
            "error": consonant_score < 70,
            "label": "Consonants / R-sound",
        },
        "vowels": {
            "score": vowel_score,
            "error": vowel_score < 70,
            "label": "Vowel Purity",
        },
        "overall_acoustic": {
            "score": dtw_score,
            "error": dtw_score < 70,
            "label": "Overall Acoustic Match",
        },
    }


def empty_score_payload(
    feedback_text: str,
    *,
    target_pronunciation: dict[str, Any] | None = None,
    pronunciation_feedback: list[dict[str, Any]] | None = None,
) -> dict:
    """
    Returns a zeroed scoring payload for attempts that fail verification.
    """
    return {
        "accuracy_score": 0.0,
        "mora_timing_score": 0.0,
        "consonant_score": 0.0,
        "vowel_score": 0.0,
        "phoneme_error_map": None,
        "feedback_text": feedback_text,
        "target_pronunciation": target_pronunciation,
        "pronunciation_feedback": pronunciation_feedback,
    }


def score_attempt(
    student_audio: bytes,
    reference_audio: bytes,
    *,
    target_text: str | None = None,
    target_romaji: str | None = None,
    pronunciation_overrides: dict[str, Any] | None = None,
    target_pronunciation: dict[str, Any] | None = None,
) -> dict:
    """
    Full scoring pipeline. When a teaching target is provided, scoring becomes
    chunk-aware and produces learner-facing pronunciation guidance.
    """
    if not target_text and target_pronunciation is None:
        return _score_attempt_legacy(student_audio, reference_audio)

    pronunciation_overrides = pronunciation_overrides or {}
    target_pronunciation = target_pronunciation or build_target_pronunciation(
        target_text or "",
        romaji_hint=target_romaji,
        reading_override=pronunciation_overrides.get("reading_override"),
        chunk_override=pronunciation_overrides.get("chunk_override"),
    )
    pronunciation_rules = build_pronunciation_rules(
        target_text or target_pronunciation.get("kana", ""),
        target_pronunciation,
        rule_override=pronunciation_overrides.get("rule_override"),
    )

    student_features = extract_features(student_audio)
    reference_features = extract_features(reference_audio)

    student_mfcc = student_features["mfcc"]
    reference_mfcc = reference_features["mfcc"]

    dtw_dist = dtw_distance(student_mfcc, reference_mfcc)
    dtw_score = dtw_to_score(dtw_dist)

    chunk_analysis = _analyze_pronunciation_chunks(
        student_features=student_features,
        reference_features=reference_features,
        target_pronunciation=target_pronunciation,
        pronunciation_rules=pronunciation_rules,
    )

    chunk_average = _average(chunk_analysis["chunk_scores"], fallback=dtw_score)
    weakest_chunk_score = min(chunk_analysis["chunk_scores"], default=dtw_score)
    timing_focus = _average(
        chunk_analysis["timing_scores"],
        fallback=chunk_average,
    )

    mora_timing_score = round(
        (score_mora_timing(student_features["duration"], reference_features["duration"]) * 0.55)
        + (timing_focus * 0.45),
        2,
    )
    consonant_score = round(
        _average(chunk_analysis["consonant_scores"], fallback=dtw_score),
        2,
    )
    vowel_score = round(
        _average(chunk_analysis["vowel_scores"], fallback=dtw_score),
        2,
    )

    chunk_consistency_score = (chunk_average * 0.65) + (weakest_chunk_score * 0.35)
    issue_penalty = sum(
        max(0.0, 88.0 - float(item["score"])) * 0.08
        for item in chunk_analysis["feedback"][:2]
    )
    accuracy_score = round(
        max(
            0.0,
            (
                (chunk_consistency_score * 0.30)
                + (mora_timing_score * 0.25)
                + (consonant_score * 0.20)
                + (vowel_score * 0.15)
                + (dtw_score * 0.10)
            ) - issue_penalty
        ),
        2,
    )

    feedback_text = (
        "Excellent pronunciation! You matched the target naturally and kept the phrase stable."
        if accuracy_score >= 90 and not chunk_analysis["feedback"]
        else summarize_pronunciation_feedback(chunk_analysis["feedback"])
    )

    phoneme_error_map = build_phoneme_error_map(
        mora_timing_score,
        consonant_score,
        vowel_score,
        dtw_score,
    )

    return {
        "accuracy_score": accuracy_score,
        "mora_timing_score": mora_timing_score,
        "consonant_score": consonant_score,
        "vowel_score": vowel_score,
        "phoneme_error_map": phoneme_error_map,
        "feedback_text": feedback_text,
        "target_pronunciation": target_pronunciation,
        "pronunciation_feedback": chunk_analysis["feedback"],
    }


def _score_attempt_legacy(student_audio: bytes, reference_audio: bytes) -> dict:
    student_features = extract_features(student_audio)
    reference_features = extract_features(reference_audio)

    student_mfcc = student_features["mfcc"]
    reference_mfcc = reference_features["mfcc"]

    dtw_dist = dtw_distance(student_mfcc, reference_mfcc)
    dtw_score = dtw_to_score(dtw_dist)

    mora_timing_score = score_mora_timing(
        student_features["duration"],
        reference_features["duration"],
    )
    consonant_score = score_consonants(student_mfcc, reference_mfcc)
    vowel_score = score_vowels(student_mfcc, reference_mfcc)

    accuracy_score = round(
        (dtw_score * 0.10)
        + (mora_timing_score * 0.35)
        + (consonant_score * 0.35)
        + (vowel_score * 0.20),
        2,
    )

    phoneme_error_map = build_phoneme_error_map(
        mora_timing_score,
        consonant_score,
        vowel_score,
        dtw_score,
    )

    feedback_parts: list[str] = []
    if mora_timing_score < 70:
        feedback_parts.append(
            "Match the phrase rhythm more closely and avoid rushing or dragging the mora timing."
        )
    if consonant_score < 70:
        feedback_parts.append(
            "Consonant clarity needs work, especially crisp Japanese consonants and r-sounds."
        )
    if vowel_score < 70:
        feedback_parts.append(
            "Keep the Japanese vowels pure and steady without sliding between sounds."
        )

    feedback_text = (
        "Excellent pronunciation! Great consistency - keep practicing to maintain this level."
        if accuracy_score >= 85
        else " ".join(feedback_parts)
        if feedback_parts
        else "Good pronunciation! Focus on consistency and natural speaking rhythm."
        if accuracy_score >= 70
        else "Keep practicing - listen to the reference audio carefully and try to match the rhythm."
    )

    return {
        "accuracy_score": accuracy_score,
        "mora_timing_score": mora_timing_score,
        "consonant_score": consonant_score,
        "vowel_score": vowel_score,
        "phoneme_error_map": phoneme_error_map,
        "feedback_text": feedback_text,
        "target_pronunciation": None,
        "pronunciation_feedback": [],
    }


def _analyze_pronunciation_chunks(
    *,
    student_features: dict[str, Any],
    reference_features: dict[str, Any],
    target_pronunciation: dict[str, Any],
    pronunciation_rules: list[Any],
) -> dict[str, Any]:
    chunks = target_pronunciation.get("chunks", [])
    chunk_count = len(chunks)
    if chunk_count == 0:
        return {
            "chunk_scores": [],
            "consonant_scores": [],
            "vowel_scores": [],
            "timing_scores": [],
            "feedback": [],
        }

    student_mfcc_slices = _segment_sequence(student_features["mfcc"], chunk_count)
    reference_mfcc_slices = _segment_sequence(reference_features["mfcc"], chunk_count)
    student_waveform_slices = _segment_waveform(student_features["waveform"], chunk_count)
    reference_waveform_slices = _segment_waveform(reference_features["waveform"], chunk_count)

    chunk_scores: list[float] = []
    consonant_scores: list[float] = []
    vowel_scores: list[float] = []
    timing_scores: list[float] = []
    feedback_items: list[dict[str, Any]] = []

    for index, chunk in enumerate(chunks):
        rule = pronunciation_rules[index]
        student_slice = student_mfcc_slices[index]
        reference_slice = reference_mfcc_slices[index]

        overall_score = _safe_slice_score(student_slice, reference_slice)
        consonant_score = score_consonants(student_slice, reference_slice)
        vowel_score = score_vowels(student_slice, reference_slice)

        student_chunk_rms = _slice_rms(student_waveform_slices[index])
        reference_chunk_rms = _slice_rms(reference_waveform_slices[index])
        timing_score = overall_score

        adjusted_score = overall_score
        if rule.issue_type == "devoicing" and reference_chunk_rms > 0:
            energy_ratio = student_chunk_rms / max(reference_chunk_rms, 1e-4)
            if energy_ratio > 1.35:
                adjusted_score = max(0.0, adjusted_score - ((energy_ratio - 1.35) * 28.0))
        elif rule.issue_type == "geminate_pause" and reference_chunk_rms > 0:
            energy_ratio = student_chunk_rms / max(reference_chunk_rms, 1e-4)
            if energy_ratio > 1.40:
                adjusted_score = max(0.0, adjusted_score - ((energy_ratio - 1.40) * 24.0))

        chunk_scores.append(round(adjusted_score, 2))
        consonant_scores.append(round(consonant_score, 2))
        vowel_scores.append(round(vowel_score, 2))
        timing_scores.append(round(timing_score, 2))

        dominant_issue = _resolve_issue_type(rule.issue_type, consonant_score, vowel_score)
        if adjusted_score < rule.threshold:
            feedback_items.append(
                {
                    "chunk_index": index,
                    "display_text": chunk["display_text"],
                    "kana": chunk["kana"],
                    "romaji": chunk["romaji"],
                    "issue_type": dominant_issue,
                    "severity": _severity_label(adjusted_score),
                    "score": round(adjusted_score, 2),
                    "expected_note": rule.expected_note,
                    "heard_note": _heard_note(
                        issue_type=dominant_issue,
                        score=adjusted_score,
                        consonant_score=consonant_score,
                        vowel_score=vowel_score,
                        student_rms=student_chunk_rms,
                        reference_rms=reference_chunk_rms,
                    ),
                    "fix_tip": rule.fix_tip,
                }
            )

    feedback_items.sort(key=lambda item: item["score"])
    return {
        "chunk_scores": chunk_scores,
        "consonant_scores": consonant_scores,
        "vowel_scores": vowel_scores,
        "timing_scores": timing_scores,
        "feedback": feedback_items,
    }


def _segment_sequence(sequence: np.ndarray, segment_count: int) -> list[np.ndarray]:
    frame_count = int(sequence.shape[1]) if sequence.ndim == 2 else 0
    if frame_count <= 0:
        return [np.zeros((sequence.shape[0], 1)) for _ in range(segment_count)]

    boundaries = np.linspace(0, frame_count, segment_count + 1)
    slices: list[np.ndarray] = []
    for index in range(segment_count):
        start = int(boundaries[index])
        end = int(boundaries[index + 1])
        start = min(start, frame_count - 1)
        end = min(max(end, start + 1), frame_count)
        slices.append(sequence[:, start:end])
    return slices


def _segment_waveform(waveform: np.ndarray, segment_count: int) -> list[np.ndarray]:
    sample_count = int(waveform.shape[0]) if waveform.ndim == 1 else 0
    if sample_count <= 0:
        return [np.zeros(1, dtype=np.float32) for _ in range(segment_count)]

    boundaries = np.linspace(0, sample_count, segment_count + 1)
    slices: list[np.ndarray] = []
    for index in range(segment_count):
        start = int(boundaries[index])
        end = int(boundaries[index + 1])
        start = min(start, sample_count - 1)
        end = min(max(end, start + 1), sample_count)
        slices.append(waveform[start:end])
    return slices


def _safe_slice_score(student_slice: np.ndarray, reference_slice: np.ndarray) -> float:
    if student_slice.size == 0 or reference_slice.size == 0:
        return 0.0
    if student_slice.shape[1] < 2 or reference_slice.shape[1] < 2:
        return 100.0 if student_slice.shape == reference_slice.shape else 70.0
    return dtw_to_score(dtw_distance(student_slice, reference_slice))


def _slice_rms(waveform: np.ndarray) -> float:
    if waveform.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(waveform))))


def _average(values: list[float], *, fallback: float) -> float:
    return float(mean(values)) if values else float(fallback)


def _resolve_issue_type(
    rule_issue_type: str,
    consonant_score: float,
    vowel_score: float,
) -> str:
    if rule_issue_type in {
        "devoicing",
        "long_vowel",
        "geminate_pause",
        "particle_pronunciation",
        "mora_nasal",
        "contracted_sound",
        "r_sound",
    }:
        return rule_issue_type

    if consonant_score + 6 < vowel_score:
        return "consonant_quality"
    if vowel_score + 6 < consonant_score:
        return "vowel_quality"
    return rule_issue_type


def _severity_label(score: float) -> str:
    if score < 55:
        return "high"
    if score < 75:
        return "medium"
    return "low"


def _heard_note(
    *,
    issue_type: str,
    score: float,
    consonant_score: float,
    vowel_score: float,
    student_rms: float,
    reference_rms: float,
) -> str:
    if issue_type == "devoicing":
        if reference_rms > 0 and student_rms > reference_rms * 1.35:
            return "This ending sounded stronger and more fully voiced than the softer native-like version."
        return "This ending did not stay light enough."

    if issue_type == "geminate_pause":
        return "The pause before the next consonant was not clear enough."

    if issue_type == "long_vowel":
        return "This long vowel did not sound fully stretched across the full beat."

    if issue_type == "particle_pronunciation":
        return "This chunk sounded closer to the written kana than the spoken particle pronunciation."

    if issue_type == "mora_nasal":
        return "The nasal mora blended too much with the surrounding vowels."

    if issue_type == "contracted_sound":
        return "This blended sound was broken apart instead of staying compact."

    if issue_type == "r_sound":
        return "The r-sound was heavier than a light Japanese flap."

    if issue_type == "consonant_quality":
        if consonant_score < vowel_score:
            return "The consonant part of this chunk was less clear than the vowel."
        return "This chunk needs cleaner consonant control."

    if issue_type == "vowel_quality":
        if vowel_score < consonant_score:
            return "The vowel in this chunk drifted away from a steady Japanese vowel."
        return "This chunk needs a steadier vowel."

    return (
        "This chunk needs a closer match to the target pronunciation."
        if score < 75
        else "This chunk is close, but it still needs a cleaner match."
    )
