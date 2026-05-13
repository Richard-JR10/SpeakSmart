from __future__ import annotations

import json
import logging
import os
import tempfile
from statistics import mean
from typing import Any

import numpy as np
import scipy.io.wavfile as wavfile

from app.config import settings
from app.services.phoneme_assessment import (
    CONSONANT_ISSUE,
    DEVOICING_ISSUE,
    GEMINATE_ISSUE,
    LONG_VOWEL_ISSUE,
    NASAL_ISSUE,
    R_SOUND_ISSUE,
    VOWEL_ISSUE,
    _apply_rule_issue_types,
    _average,
    _build_feedback,
    _duration_score,
    _fluency_score,
    _optional_text,
    _score_morae,
    _severity_label,
    _slow_practice_text,
    _student_guidance,
    _weighted_average,
    enrich_target_pronunciation,
)
from app.services.speech import load_audio_from_bytes, prepare_waveform


logger = logging.getLogger("speaksmart.azure_pronunciation")

_HUNDRED_NS = 10_000_000  # 100-nanosecond ticks per second


def score_attempt_azure(
    student_audio: bytes,
    reference_audio: bytes,
    *,
    target_text: str,
    target_pronunciation: dict[str, Any],
    pronunciation_rules: list[Any],
) -> dict[str, Any]:
    from app.services.speech import extract_features

    student_features = extract_features(student_audio)
    reference_features = extract_features(reference_audio)

    enriched_target = enrich_target_pronunciation(target_pronunciation)
    enriched_target = _apply_rule_issue_types(enriched_target, pronunciation_rules)
    expected_phonemes = enriched_target.get("phonemes", [])
    mora_targets = enriched_target.get("morae", [])

    azure_result = _call_azure_assessment(student_audio, target_text)

    phone_details = _map_azure_phonemes(
        azure_result=azure_result,
        expected_phonemes=expected_phonemes,
        reference_duration=reference_features["duration"],
        student_duration=student_features["duration"],
    )
    mora_details = _score_morae(
        mora_targets=mora_targets,
        phone_details=phone_details,
        pronunciation_rules=pronunciation_rules,
    )
    feedback = _build_feedback(
        mora_details=mora_details,
        phone_details=phone_details,
        pronunciation_rules=pronunciation_rules,
    )[:2]

    overall_accuracy = float(azure_result.get("accuracy_score", 0))
    phoneme_match_score = _weighted_average(
        [item["score"] for item in phone_details],
        [float(item.get("weight", 1.0)) for item in phone_details],
        fallback=overall_accuracy,
    )
    mora_timing_score = _average(
        [item["duration_score"] for item in mora_details],
        fallback=_duration_score(
            student_features["duration"], reference_features["duration"]
        ),
    )
    consonant_score = _average(
        [
            item["score"]
            for item in phone_details
            if item["type"] in {"consonant", "glide", "nasal", "pause"}
        ],
        fallback=overall_accuracy,
    )
    vowel_score = _average(
        [item["score"] for item in phone_details if item["type"] == "vowel"],
        fallback=overall_accuracy,
    )
    fluency_score = float(azure_result.get("fluency_score", 0))

    # Pitch accent scoring — uses pyopenjtalk for reference pattern and
    # parselmouth for F0 extraction. Falls back to None when unavailable.
    from app.services.pitch_accent import (  # noqa: PLC0415
        extract_mora_f0,
        get_reference_accent_pattern,
        score_pitch_accent,
    )
    mora_timestamps = _build_mora_timestamps(phone_details)
    reference_pattern = get_reference_accent_pattern(target_text)
    student_f0s = extract_mora_f0(student_audio, mora_timestamps)
    pitch_result = score_pitch_accent(reference_pattern, student_f0s)
    pitch_accent_score = pitch_result["pitch_accent_score"]

    recognizer = {
        "provider": "azure_pronunciation_assessment",
        "ctc_enabled": True,
        "fallback_used": False,
        "warning": None,
        "confidence": min(1.0, overall_accuracy / 100.0),
        "elapsed_ms": None,
    }

    return {
        "target_pronunciation": enriched_target,
        "phoneme_match_score": round(phoneme_match_score, 2),
        "mora_timing_score": round(mora_timing_score, 2),
        "consonant_score": round(consonant_score, 2),
        "vowel_score": round(vowel_score, 2),
        "fluency_score": round(fluency_score, 2),
        "pitch_accent_score": round(pitch_accent_score, 2) if pitch_accent_score is not None else None,
        "pitch_accent_errors": pitch_result["mora_pitch_errors"],
        "phonemes": phone_details,
        "morae": mora_details,
        "feedback": feedback,
        "recognizer": recognizer,
    }


def _call_azure_assessment(audio_bytes: bytes, reference_text: str) -> dict[str, Any]:
    import azure.cognitiveservices.speech as speechsdk

    key = settings.AZURE_SPEECH_KEY
    region = settings.AZURE_SPEECH_REGION
    if not key or not region:
        raise RuntimeError("AZURE_SPEECH_KEY and AZURE_SPEECH_REGION must be set.")

    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.speech_recognition_language = "ja-JP"

    tmp_path = _write_wav_tempfile(audio_bytes)
    try:
        audio_config = speechsdk.audio.AudioConfig(filename=tmp_path)
        pronunciation_config = speechsdk.PronunciationAssessmentConfig(
            reference_text=reference_text,
            grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
            granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
            enable_miscue=True,
        )
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            language="ja-JP",
            audio_config=audio_config,
        )
        pronunciation_config.apply_to(recognizer)
        result = recognizer.recognize_once()
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        pa_result = speechsdk.PronunciationAssessmentResult(result)
        raw = json.loads(result.json)
        words = raw.get("NBest", [{}])[0].get("Words", [])
        return {
            "accuracy_score": float(pa_result.accuracy_score or 0),
            "fluency_score": float(pa_result.fluency_score or 0),
            "completeness_score": float(pa_result.completeness_score or 0),
            "words": words,
        }
    elif result.reason == speechsdk.ResultReason.NoMatch:
        logger.warning("Azure: no speech matched for text=%s", reference_text)
        return {
            "accuracy_score": 0.0,
            "fluency_score": 0.0,
            "completeness_score": 0.0,
            "words": [],
        }
    else:
        raise RuntimeError(f"Azure speech recognition failed: {result.reason}")


def _write_wav_tempfile(audio_bytes: bytes) -> str:
    y, sr = load_audio_from_bytes(audio_bytes)
    y = prepare_waveform(y)
    y_int16 = np.clip(y * 32767.0, -32768, 32767).astype(np.int16)
    fd, tmp_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    wavfile.write(tmp_path, 16000, y_int16)
    return tmp_path


def _align_azure_slots(
    slots: list[dict[str, Any]],
    expected_count: int,
) -> list[dict[str, Any]]:
    # Strip insertion slots — extra sounds the student made that have no
    # expected phoneme counterpart. Without this, one Azure insertion shifts
    # every subsequent expected phoneme to the wrong slot.
    mapped = [s for s in slots if s.get("operation") != "insertion"]
    result: list[dict[str, Any]] = []
    for i in range(expected_count):
        if i < len(mapped):
            result.append(mapped[i])
        else:
            result.append({"score": 15.0, "duration_s": 0.0, "offset_s": 0.0, "operation": "deletion"})
    return result


def _map_azure_phonemes(
    *,
    azure_result: dict[str, Any],
    expected_phonemes: list[dict[str, Any]],
    reference_duration: float,
    student_duration: float,
) -> list[dict[str, Any]]:
    if not expected_phonemes:
        return []

    total_weight = sum(max(0.1, float(p.get("weight", 1.0))) for p in expected_phonemes)
    ref_dur_per_phoneme = {
        p["index"]: (max(0.1, float(p.get("weight", 1.0))) / total_weight) * reference_duration
        for p in expected_phonemes
    }

    raw_slots = _flatten_azure_slots(azure_result.get("words", []))
    azure_slots = _align_azure_slots(raw_slots, len(expected_phonemes))

    phone_details: list[dict[str, Any]] = []
    for i, expected in enumerate(expected_phonemes):
        slot = azure_slots[i]

        score = float(slot.get("score", 0.0))
        operation = str(slot.get("operation", "match"))
        if operation == "match" and score < 78.0:
            operation = "substitution"
        elif score < 20.0:
            operation = "deletion"

        phone_type = str(expected.get("type", "consonant"))
        issue_type = str(expected.get("issue_type", CONSONANT_ISSUE))
        ref_dur = ref_dur_per_phoneme.get(int(expected["index"]), 0.1)
        student_dur = float(slot.get("duration_s", 0.0))
        student_offset = float(slot.get("offset_s", 0.0))
        duration_score = _duration_score(student_dur, ref_dur)

        detail_issue = _detail_issue_type(
            phone_type=phone_type,
            issue_type=issue_type,
            score=score,
            operation=operation,
        )
        heard_phoneme, heard_label = _heard_sound(
            expected=str(expected.get("symbol", "")),
            label=str(expected.get("label", "")),
            score=score,
            operation=operation,
        )

        phone_details.append(
            {
                "index": int(expected["index"]),
                "mora_index": int(expected["mora_index"]),
                "chunk_index": int(expected["chunk_index"]),
                "kana": str(expected["kana"]),
                "romaji": str(expected["romaji"]),
                "expected_phoneme": str(expected["symbol"]),
                "expected_label": str(expected["label"]),
                "heard_phoneme": heard_phoneme,
                "heard_label": heard_label,
                "type": phone_type,
                "target_issue_type": issue_type,
                "issue_type": detail_issue,
                "operation": operation,
                "score": round(score, 2),
                "error": score < 78.0,
                "weight": float(expected.get("weight", 1.0)),
                "duration_score": round(duration_score, 2),
                "student_offset_ms": round(student_offset * 1000.0, 1),
                "student_duration_ms": round(student_dur * 1000.0, 1),
                "reference_duration_ms": round(ref_dur * 1000.0, 1),
                "reference_frame_start": 0,
                "reference_frame_end": 0,
                "student_frame_start": 0,
                "student_frame_end": 0,
            }
        )

    return phone_details


def _flatten_azure_slots(words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    for word in words:
        error_type = word.get("PronunciationAssessment", {}).get("ErrorType", "None")
        phonemes_in_word = word.get("Phonemes", [])

        if error_type == "Omission":
            for _ in phonemes_in_word or [None]:
                slots.append({"score": 0.0, "duration_s": 0.0, "offset_s": 0.0, "operation": "deletion"})
            continue

        for phone in phonemes_in_word:
            score = float(phone.get("PronunciationAssessment", {}).get("AccuracyScore", 0))
            offset_s = int(phone.get("Offset", 0)) / _HUNDRED_NS
            duration_s = int(phone.get("Duration", 0)) / _HUNDRED_NS
            operation = "deletion" if score < 20 else "substitution" if score < 78 else "match"
            if error_type == "Insertion":
                operation = "insertion"
            slots.append({"score": score, "duration_s": duration_s, "offset_s": offset_s, "operation": operation})

    return slots


def _detail_issue_type(
    *,
    phone_type: str,
    issue_type: str,
    score: float,
    operation: str,
) -> str:
    if operation == "match" and score >= 78.0:
        return "match"
    if operation == "deletion":
        return "deletion"
    if issue_type == LONG_VOWEL_ISSUE:
        return "long_vowel_issue"
    if issue_type == GEMINATE_ISSUE:
        return "geminate_issue"
    if issue_type == NASAL_ISSUE:
        return "nasal_issue"
    if issue_type == R_SOUND_ISSUE:
        return "r_flap_issue"
    if issue_type == DEVOICING_ISSUE:
        return "devoicing_issue"
    if phone_type == "vowel":
        return "vowel_drift"
    return "substitution"


def _heard_sound(
    *,
    expected: str,
    label: str,
    score: float,
    operation: str,
) -> tuple[str, str]:
    if operation == "match":
        return expected, label
    if operation == "deletion":
        return "omitted", "omitted or clipped"
    if score < 62.0:
        return "unclear", "unclear sound"
    return expected, f"unstable {label}"


def _build_mora_timestamps(
    phone_details: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Groups per-phoneme Azure timestamps by mora_index to produce per-mora
    time windows for F0 extraction.
    """
    mora_map: dict[int, dict[str, Any]] = {}
    for phone in phone_details:
        mora_idx = int(phone["mora_index"])
        offset_ms = float(phone.get("student_offset_ms", 0.0))
        duration_ms = float(phone.get("student_duration_ms", 0.0))
        if mora_idx not in mora_map:
            mora_map[mora_idx] = {
                "mora_index": mora_idx,
                "offset_ms": offset_ms,
                "duration_ms": duration_ms,
            }
        else:
            existing = mora_map[mora_idx]
            start = min(existing["offset_ms"], offset_ms)
            end = max(
                existing["offset_ms"] + existing["duration_ms"],
                offset_ms + duration_ms,
            )
            existing["offset_ms"] = start
            existing["duration_ms"] = end - start

    return [mora_map[k] for k in sorted(mora_map)]
