import numpy as np
from scipy.spatial.distance import cdist

from app.services.speech import extract_features


def normalize_feature_sequence(seq: np.ndarray) -> np.ndarray:
    """
    Normalize each MFCC coefficient to zero mean and unit variance so the
    comparison is less sensitive to microphone gain and voice timbre.
    """
    mean = np.mean(seq, axis=1, keepdims=True)
    std = np.std(seq, axis=1, keepdims=True)
    return (seq - mean) / np.maximum(std, 1e-6)


def dtw_distance(seq_a: np.ndarray, seq_b: np.ndarray) -> float:
    """
    Computes the normalized DTW distance between two MFCC sequences.

    Args:
        seq_a - shape (n_mfcc, T1) student audio features
        seq_b - shape (n_mfcc, T2) reference audio features

    Returns:
        Normalized DTW distance (lower = more similar)
    """
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

    The previous mapping reached 0 too quickly for real learner recordings
    against a TTS reference. This version degrades more gradually so normal
    human pronunciation still produces a useful non-zero score.
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

    +/-15% around the reference is treated as fully correct, then the score
    declines linearly until a 60% deviation where it reaches 0.
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

    dist = dtw_distance(upper_student, upper_reference)
    return dtw_to_score(dist)


def score_vowels(student_mfcc: np.ndarray, reference_mfcc: np.ndarray) -> float:
    """
    Scores vowel purity using lower MFCC bands (coefficients 1-5).
    """
    lower_student = student_mfcc[1:6, :]
    lower_reference = reference_mfcc[1:6, :]

    dist = dtw_distance(lower_student, lower_reference)
    return dtw_to_score(dist)


def build_phoneme_error_map(
    mora_timing_score: float,
    consonant_score: float,
    vowel_score: float,
    dtw_score: float,
) -> dict:
    """
    Builds a per-phoneme error flag dictionary for the frontend.
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


def generate_feedback(
    mora_timing_score: float,
    consonant_score: float,
    vowel_score: float,
    overall_score: float,
) -> str:
    """
    Generates a human-readable feedback message based on the weakest component.
    """
    if overall_score >= 85:
        return (
            "Excellent pronunciation! Great consistency - keep practicing to "
            "maintain this level."
        )

    messages = []

    if mora_timing_score < 70:
        messages.append(
            "Match the phrase rhythm more closely - avoid speaking much faster or slower than the reference."
        )
    if consonant_score < 70:
        messages.append(
            "Consonant clarity needs work - especially crisp Japanese consonants and the R-sound."
        )
    if vowel_score < 70:
        messages.append(
            "Keep Japanese vowels short and pure - avoid sliding between vowel sounds."
        )

    if not messages:
        if overall_score >= 70:
            return "Good pronunciation! Focus on consistency and natural speaking rhythm."
        return "Keep practicing - listen to the reference audio carefully and try to match the rhythm."

    return " ".join(messages)


def score_attempt(student_audio: bytes, reference_audio: bytes) -> dict:
    """
    Full scoring pipeline. Called once per attempt submission.
    """
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
    feedback_text = generate_feedback(
        mora_timing_score,
        consonant_score,
        vowel_score,
        accuracy_score,
    )

    return {
        "accuracy_score": accuracy_score,
        "mora_timing_score": mora_timing_score,
        "consonant_score": consonant_score,
        "vowel_score": vowel_score,
        "phoneme_error_map": phoneme_error_map,
        "feedback_text": feedback_text,
    }
