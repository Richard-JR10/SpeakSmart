from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger("speaksmart.pitch_accent")

_SAMPLE_RATE = 16000
_MIN_F0 = 75.0    # Hz — below this is likely unvoiced or noise
_MIN_VOICED_FRAMES = 3  # parselmouth frames; fewer than this → treat as unvoiced


def get_reference_accent_pattern(text: str) -> list[dict[str, Any]]:
    """
    Returns expected pitch pattern per mora using pyopenjtalk (MARINE model).
    Each entry: {"mora": str, "pitch": "H" | "L", "accent_nucleus": bool}

    Returns [] gracefully when pyopenjtalk is unavailable (ImportError) or the
    text cannot be analysed.  Callers should treat [] as "no pitch data".
    """
    try:
        import pyopenjtalk  # noqa: PLC0415
    except ImportError:
        logger.debug("pyopenjtalk not available — pitch accent skipped")
        return []

    try:
        # run_frontend returns one dict per token with "acc" (accent nucleus mora
        # index from the start of the accent phrase, 0 = flat/undecided) and
        # "pron" (katakana pronunciation string).
        tokens = pyopenjtalk.run_frontend(text)
    except Exception:
        logger.exception("pyopenjtalk.run_frontend failed for text=%r", text)
        return []

    pattern: list[dict[str, Any]] = []
    for token in tokens:
        pron: str = token.get("pron", "") or ""
        acc: int = int(token.get("acc", 0))
        if not pron:
            continue

        morae = _katakana_to_morae(pron)
        n = len(morae)

        for mora_pos, mora in enumerate(morae):
            if acc == 0:
                # Flat (heiban): low on mora 1, high on all others
                pitch = "L" if mora_pos == 0 else "H"
                nucleus = False
            elif mora_pos < acc:
                # Before nucleus: mora 0 is L, morae 1…acc-1 are H
                pitch = "L" if mora_pos == 0 else "H"
                nucleus = mora_pos == acc - 1
            else:
                # At or after nucleus drop
                pitch = "L"
                nucleus = mora_pos == acc

            pattern.append({
                "mora": mora,
                "pitch": pitch,
                "accent_nucleus": nucleus,
                "token_mora_pos": mora_pos,
                "accent_type": acc,
                "n_morae_in_token": n,
            })

    return pattern


def extract_mora_f0(
    audio_bytes: bytes,
    mora_timestamps: list[dict[str, Any]],
) -> list[float | None]:
    """
    Returns mean F0 (Hz) per mora, or None when the mora is unvoiced.

    mora_timestamps: list of {"mora_index": int, "offset_ms": float, "duration_ms": float}
    Morae are expected to be in mora_index order.
    """
    try:
        import parselmouth  # noqa: PLC0415
    except ImportError:
        logger.debug("parselmouth not available — F0 extraction skipped")
        return [None] * len(mora_timestamps)

    try:
        from app.services.speech import load_audio_from_bytes  # noqa: PLC0415
        y, sr = load_audio_from_bytes(audio_bytes)
    except Exception:
        logger.exception("Failed to load audio for F0 extraction")
        return [None] * len(mora_timestamps)

    try:
        snd = parselmouth.Sound(values=y.astype(np.float64), sampling_frequency=float(sr))
        pitch_track = snd.to_pitch(time_step=0.01, pitch_floor=_MIN_F0, pitch_ceiling=600.0)
    except Exception:
        logger.exception("parselmouth pitch extraction failed")
        return [None] * len(mora_timestamps)

    results: list[float | None] = []
    for ts in mora_timestamps:
        offset_s = float(ts.get("offset_ms", 0.0)) / 1000.0
        duration_s = float(ts.get("duration_ms", 0.0)) / 1000.0
        if duration_s < 0.015:
            results.append(None)
            continue
        try:
            t_start = offset_s
            t_end = offset_s + duration_s
            frames = [
                pitch_track.get_value_at_time(t)
                for t in np.arange(t_start + 0.005, t_end - 0.005, 0.01)
                if t_start < t < t_end
            ]
            voiced = [f for f in frames if f is not None and not np.isnan(f) and f > _MIN_F0]
            if len(voiced) < _MIN_VOICED_FRAMES:
                results.append(None)
            else:
                results.append(float(np.median(voiced)))
        except Exception:
            results.append(None)

    return results


def score_pitch_accent(
    reference_pattern: list[dict[str, Any]],
    student_f0s: list[float | None],
) -> dict[str, Any]:
    """
    Compares the student F0 contour to the expected H/L pattern.

    Returns:
      pitch_accent_score  float  0–100
      mora_pitch_errors   list[int]  mora indexes where pitch direction was wrong
      pattern_match_ratio float  fraction of comparable mora pairs that matched
    """
    if not reference_pattern or not student_f0s:
        return {
            "pitch_accent_score": None,
            "mora_pitch_errors": [],
            "pattern_match_ratio": None,
        }

    n = min(len(reference_pattern), len(student_f0s))
    voiced_pairs: list[tuple[int, str, float]] = []  # (mora_index, expected_pitch, f0)

    for i in range(n):
        f0 = student_f0s[i]
        if f0 is not None:
            voiced_pairs.append((i, reference_pattern[i]["pitch"], f0))

    if len(voiced_pairs) < 2:
        return {
            "pitch_accent_score": None,
            "mora_pitch_errors": [],
            "pattern_match_ratio": None,
        }

    # Score pitch TRANSITIONS between consecutive voiced morae rather than
    # classifying each mora as H or L against a speaker-dependent threshold.
    #
    # Japanese pitch accent is defined by where the pitch rises (L→H) and
    # where it drops (H→L). H→H and L→L pairs carry no contrastive information
    # and are skipped so they don't dilute the score.
    #
    # An 8% F0 ratio threshold separates meaningful transitions from
    # natural jitter within a single pitch level.
    _RISE_THRESHOLD = 1.08   # f0_next / f0_prev > 1.08 → rising
    _FALL_THRESHOLD = 0.92   # f0_next / f0_prev < 0.92 → falling

    errors: list[int] = []
    correct = 0
    total = 0

    for k in range(1, len(voiced_pairs)):
        prev_idx, prev_pitch, prev_f0 = voiced_pairs[k - 1]
        curr_idx, curr_pitch, curr_f0 = voiced_pairs[k]

        # Only evaluate transitions between adjacent morae (not across voiceless gaps).
        if curr_idx != prev_idx + 1:
            continue

        expected_rise = (prev_pitch == "L" and curr_pitch == "H")
        expected_fall = (prev_pitch == "H" and curr_pitch == "L")

        if not expected_rise and not expected_fall:
            # Same-level transition (H→H or L→L) — skip, no penalty.
            continue

        ratio_f0 = curr_f0 / prev_f0 if prev_f0 > 0 else 1.0
        student_rising = ratio_f0 > _RISE_THRESHOLD
        student_falling = ratio_f0 < _FALL_THRESHOLD

        if expected_rise:
            if student_rising:
                correct += 1
            else:
                errors.append(curr_idx)
        else:  # expected_fall
            if student_falling:
                correct += 1
            else:
                errors.append(curr_idx)
        total += 1

    if total == 0:
        # No scoreable transitions (e.g. flat accent phrase with all H→H).
        # Return a neutral score rather than None so the row still appears.
        return {
            "pitch_accent_score": 75.0,
            "mora_pitch_errors": [],
            "pattern_match_ratio": None,
        }

    ratio = correct / total
    score = ratio * 100.0

    return {
        "pitch_accent_score": round(score, 2),
        "mora_pitch_errors": errors,
        "pattern_match_ratio": round(ratio, 3),
    }


def _katakana_to_morae(text: str) -> list[str]:
    """Split a katakana string into individual morae (handles long vowels and digraphs)."""
    _SMALL = frozenset("ァィゥェォャュョヮヵヶぁぃぅぇぉゃゅょゎ")
    morae: list[str] = []
    for ch in text:
        if ch in _SMALL and morae:
            morae[-1] += ch
        else:
            morae.append(ch)
    return morae
