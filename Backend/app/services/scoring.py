import numpy as np
from scipy.spatial.distance import cdist
from app.services.speech import extract_features

#── DTW ──
def dtw_distance(seq_a: np.ndarray, seq_b: np.ndarray) -> float:
    """
    Computes the normalized DTW distance between two MFCC sequences.

    Args:
        seq_a — shape (n_mfcc, T1)  student audio features
        seq_b — shape (n_mfcc, T2)  reference audio features

    Returns:
        Normalized DTW distance (lower = more similar)
    """
    #Transpose to (T, n_mfcc) for cdist
    a = seq_a.T
    b = seq_b.T

    # Pairwise Euclidean cost matrix
    cost_matrix = cdist(a, b, metric='euclidean')

    T1, T2 = cost_matrix.shape
    accumulated = np.full((T1, T2), np.inf)
    accumulated[0, 0] = cost_matrix[0, 0]

    # Fill first row and column
    for i in range(1, T1):
        accumulated[i, 0] = accumulated[i-1, 0] + cost_matrix[i, 0]
    for j in range(1, T2):
        accumulated[0, j] = accumulated[0, j-1] + cost_matrix[0, j]

    # Fill rest of matrix
    for i in range(1, T1):
        for j in range(1, T2):
            accumulated[i, j] = cost_matrix[i, j] + min(
                accumulated[i-1, j],    # insertion
                accumulated[i, j-1],    # deletion
                accumulated[i-1, j-1]   # match
            )

    # Normalize by path length to avoid penelizing longer utterances
    normalized = accumulated[T1 - 1, T2 - 1] / (T1 + T2)
    return float(normalized)

def dtw_to_score(dtw_dist: float) -> float:
    """
    Converts a raw DTW distance to a 0–100 score.
    Tuned empirically for Japanese MFCC comparisons at 16kHz.

    Distance thresholds:
        0.0  → 100% (perfect match)
        3.0  → ~50% (poor match)
        6.0+ →   0% (no similarity)
    """
    score = max(0.0, 100.0 - (dtw_dist * 16.0))
    return round(min(score, 100.0), 2)

#── Component Scorers ──

def score_mora_timing(student_duration: float, reference_duration: float) -> float:
    """
    Scores mora timing accuracy based on duration ratio.

    Japanese is mora-timed — each mora should take equal duration.
    Filipino learners often rush through long vowels.

    Scoring:
        ratio 0.85–1.15  → 100% (within ±15% is natural variation)
        ratio 0.70–1.30  → scaled linearly
        outside 0.70–1.30 → 0%
    """
    if reference_duration <= 0:
        return 100.0

    ratio = student_duration / reference_duration
    
    if 0.85 <= ratio <= 1.15:
        return 100.0
    elif 0.70 <= ratio < 0.85:
        return round((ratio - 0.70) / (0.85 - 0.70) * 100, 2)
    elif 1.15 < ratio <= 1.30:
        return round((1.30 - ratio) / (1.30 - 1.15) * 100, 2)
    else:
        return 0.0
    
def score_consonants(student_mfcc: np.ndarray, reference_mfcc: np.ndarray) -> float:
    """
    Scores consonant accuracy using upper MFCC bands (coefficients 6–12).

    Upper MFCC coefficients capture fine spectral detail — consonant
    articulation, including the Japanese R-sound (ら り る れ ろ).
    """
    upper_student = student_mfcc[6:, :]
    upper_reference = reference_mfcc[6:, :]

    dist = dtw_distance(upper_student, upper_reference)
    return dtw_to_score(dist)

def score_vowels(student_mfcc: np.ndarray, reference_mfcc: np.ndarray) -> float:
    """
    Scores vowel purity using lower MFCC bands (coefficients 1–5).

    Lower MFCC coefficients capture broad spectral shape — vowel
    formant structure. Japanese has only 5 pure vowels with no
    diphthong drift, which is a common error for Filipino speakers.
    """
    lower_student = student_mfcc[1:6, :]
    lower_reference = reference_mfcc[1:6, :]

    dist = dtw_distance(lower_student, lower_reference)
    return dtw_to_score(dist)

# ── Phoneme error map ──

def build_phoneme_error_map(
    mora_timing_score: float,
    consonant_score: float,
    vowel_score: float,
    dtw_score: float
) -> dict:
    """
    Builds a per-phoneme error flag dictionary for the frontend
    to render phoneme chip highlights (green = good, red = error).
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

# ── Feedback generator ──
def generate_feedback(
    mora_timing_score: float,
    consonant_score: float,
    vowel_score: float,
    overall_score: float,
) -> str:
    """
    Generates a human-readable feedback message based on the
    weakest scoring component. Priority: mora > consonant > vowel.
    """
    if overall_score >= 85:
        return "Excellent pronunciation! Great consistency — keep practicing to maintain this level."

    messages = []

    if mora_timing_score < 70:
        messages.append(
            "Long vowels need more duration — hold each vowel for a full mora beat."
        )
    if consonant_score < 70:
        messages.append(
            "The R-sound needs work — curl the tongue slightly and let it flap lightly."
        )
    if vowel_score < 70:
        messages.append(
            "Keep Japanese vowels pure — avoid the diphthong drift common in Filipino speech."
        )

    if not messages:
        if overall_score >= 70:
            return "Good pronunciation! Focus on consistency and natural speaking rhythm."
        else:
            return "Keep practicing — listen to the reference audio carefully and try to match the rhythm."

    return " ".join(messages)

# ── Main scoring pipeline ──
def score_attempt(student_audio: bytes, reference_audio: bytes) -> dict:
    """
    Full scoring pipeline. Called once per attempt submission.

    Args:
        student_audio   — raw bytes of student recording
        reference_audio — raw bytes of reference TTS audio from R2

    Returns dict with:
        accuracy_score      — weighted overall score (0–100)
        mora_timing_score   — duration accuracy score (0–100)
        consonant_score     — upper MFCC / R-sound score (0–100)
        vowel_score         — lower MFCC / vowel purity score (0–100)
        phoneme_error_map   — per-component error flags
        feedback_text       — human-readable feedback string
    """
    # 1. Extract features for both audio files
    student_features = extract_features(student_audio)
    reference_features = extract_features(reference_audio)

    student_mfcc = student_features["mfcc"]
    reference_mfcc = reference_features["mfcc"]

    # 2. Full DTW on all 13 MFCC coefficients
    dtw_dist = dtw_distance(student_mfcc, reference_mfcc)
    dtw_score = dtw_to_score(dtw_dist)

    # 3. Component scores
    mora_timing_score = score_mora_timing(
        student_features["duration"],
        reference_features["duration"],
    )
    consonant_score = score_consonants(student_mfcc, reference_mfcc)
    vowel_score = score_vowels(student_mfcc, reference_mfcc)

    # 4. Weighted overall score
    # Weighted from docs: DTW 10%, Mora 35%, Consonant 35%, Vowel 20%
    accuracy_score = round(
        (dtw_score * 0.10) +
        (mora_timing_score * 0.35) +
        (consonant_score * 0.35) +
        (vowel_score * 0.20),
        2
    )

    # 5. Phoneme error map + feedback
    phoneme_error_map = build_phoneme_error_map(
        mora_timing_score,
        consonant_score,
        vowel_score,
        dtw_score
    )
    feedback_text = generate_feedback(
        mora_timing_score,
        consonant_score,
        vowel_score,
        accuracy_score
    )

    return {
        "accuracy_score": accuracy_score,
        "mora_timing_score": mora_timing_score,
        "consonant_score": consonant_score,
        "vowel_score": vowel_score,
        "phoneme_error_map": phoneme_error_map,
        "feedback_text": feedback_text,
    }