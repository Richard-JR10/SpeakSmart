from __future__ import annotations

import logging
from dataclasses import dataclass
from statistics import mean
from typing import Any

import numpy as np
from scipy.spatial.distance import cdist

from app.config import settings


logger = logging.getLogger("speaksmart.phoneme_assessment")

VOWELS = frozenset("aeiou")
PAUSE_KANA = "\u3063"
NASAL_KANA = "\u3093"
LONG_MARK = "\u30fc"
LONG_O_KANA = "\u3046"
LONG_I_KANA = "\u3044"
SMALL_Y_KANA = frozenset(("\u3083", "\u3085", "\u3087"))
LONG_VOWEL_ISSUE = "long_vowel"
GEMINATE_ISSUE = "geminate_pause"
NASAL_ISSUE = "mora_nasal"
R_SOUND_ISSUE = "r_sound"
DEVOICING_ISSUE = "devoicing"
VOWEL_ISSUE = "vowel_quality"
CONSONANT_ISSUE = "consonant_quality"

PALATALIZED_ONSETS = (
    "ky",
    "gy",
    "ny",
    "hy",
    "by",
    "py",
    "my",
    "ry",
    "sh",
    "ch",
    "j",
)
SPECIAL_ONSETS = ("ts", "sh", "ch", "f")


@dataclass(frozen=True)
class PhoneSpec:
    symbol: str
    kind: str
    issue_type: str
    weight: float


def align_phoneme_sequences(
    expected: list[str],
    spoken: list[str],
) -> list[dict[str, Any]]:
    """
    Aligns target phonemes with a recognized phoneme stream. This is used by
    CTC-style recognizers and is kept separate from acoustic DTW alignment so
    substitutions, deletions, and insertions have explicit operations.
    """
    rows = len(expected) + 1
    columns = len(spoken) + 1
    costs = np.zeros((rows, columns), dtype=np.float32)
    backpointers: list[list[str]] = [["" for _ in range(columns)] for _ in range(rows)]

    for row in range(1, rows):
        costs[row, 0] = float(row)
        backpointers[row][0] = "deletion"
    for column in range(1, columns):
        costs[0, column] = float(column)
        backpointers[0][column] = "insertion"

    for row in range(1, rows):
        for column in range(1, columns):
            is_match = _phonemes_equivalent(expected[row - 1], spoken[column - 1])
            substitution_cost = costs[row - 1, column - 1] + (0.0 if is_match else 1.0)
            deletion_cost = costs[row - 1, column] + 1.0
            insertion_cost = costs[row, column - 1] + 1.0
            best_cost = min(substitution_cost, deletion_cost, insertion_cost)

            costs[row, column] = best_cost
            if best_cost == substitution_cost:
                backpointers[row][column] = "match" if is_match else "substitution"
            elif best_cost == deletion_cost:
                backpointers[row][column] = "deletion"
            else:
                backpointers[row][column] = "insertion"

    row = len(expected)
    column = len(spoken)
    operations: list[dict[str, Any]] = []
    while row > 0 or column > 0:
        operation = backpointers[row][column]
        if operation in {"match", "substitution"}:
            operations.append(
                {
                    "operation": operation,
                    "expected_index": row - 1,
                    "spoken_index": column - 1,
                    "expected_phoneme": expected[row - 1],
                    "heard_phoneme": spoken[column - 1],
                }
            )
            row -= 1
            column -= 1
        elif operation == "deletion":
            operations.append(
                {
                    "operation": "deletion",
                    "expected_index": row - 1,
                    "spoken_index": None,
                    "expected_phoneme": expected[row - 1],
                    "heard_phoneme": "omitted",
                }
            )
            row -= 1
        else:
            operations.append(
                {
                    "operation": "insertion",
                    "expected_index": None,
                    "spoken_index": column - 1,
                    "expected_phoneme": None,
                    "heard_phoneme": spoken[column - 1],
                }
            )
            column -= 1

    operations.reverse()
    return operations


def enrich_target_pronunciation(
    target_pronunciation: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Adds mora and phoneme targets to the existing kana/romaji/chunk payload.
    The function is deterministic and dependency-free so target generation stays
    fast and can run before audio scoring.
    """
    payload = dict(target_pronunciation or {})
    chunks = [dict(item) for item in payload.get("chunks", [])]

    morae: list[dict[str, Any]] = []
    phonemes: list[dict[str, Any]] = []
    previous_vowel = ""

    for chunk_index, chunk in enumerate(chunks):
        kana = str(chunk.get("kana", chunk.get("display_text", "")))
        romaji = _normalize_romaji(str(chunk.get("romaji", "")))
        mora_issue = _mora_issue_type(kana, romaji, previous_vowel)
        phone_specs = _phone_specs_for_mora(kana, romaji, mora_issue)
        phone_indexes: list[int] = []

        for spec in phone_specs:
            phoneme_index = len(phonemes)
            phone_indexes.append(phoneme_index)
            phonemes.append(
                {
                    "index": phoneme_index,
                    "symbol": spec.symbol,
                    "label": _phoneme_label(spec.symbol, spec.kind),
                    "type": spec.kind,
                    "mora_index": len(morae),
                    "chunk_index": chunk_index,
                    "kana": kana,
                    "romaji": romaji,
                    "issue_type": spec.issue_type,
                    "weight": spec.weight,
                }
            )

        morae.append(
            {
                "index": len(morae),
                "chunk_index": chunk_index,
                "display_text": str(chunk.get("display_text", kana)),
                "kana": kana,
                "romaji": romaji,
                "phoneme_indexes": phone_indexes,
                "phonemes": [phonemes[index]["symbol"] for index in phone_indexes],
                "issue_type": mora_issue,
            }
        )

        previous_vowel = _final_vowel_from_specs(phone_specs) or previous_vowel

    payload["chunks"] = chunks
    payload["morae"] = morae
    payload["phonemes"] = phonemes
    return payload


def assess_pronunciation(
    *,
    student_audio: bytes | None = None,
    student_features: dict[str, Any],
    reference_features: dict[str, Any],
    target_pronunciation: dict[str, Any],
    pronunciation_rules: list[Any],
    overall_acoustic_score: float,
) -> dict[str, Any]:
    """
    Scores expected Japanese phonemes and morae using a real DTW alignment path
    between the reference audio and the learner audio. This replaces equal chunk
    slicing while keeping the current reference-audio comparison workflow.
    """
    enriched_target = enrich_target_pronunciation(target_pronunciation)
    enriched_target = _apply_rule_issue_types(enriched_target, pronunciation_rules)
    phoneme_targets = enriched_target.get("phonemes", [])
    mora_targets = enriched_target.get("morae", [])
    recognizer_metadata = _recognizer_metadata()

    if not phoneme_targets:
        return {
            "target_pronunciation": enriched_target,
            "phoneme_match_score": overall_acoustic_score,
            "mora_timing_score": _duration_score(
                student_features.get("duration", 0.0),
                reference_features.get("duration", 0.0),
            ),
            "consonant_score": overall_acoustic_score,
            "vowel_score": overall_acoustic_score,
            "fluency_score": _fluency_score(student_features, reference_features),
            "phonemes": [],
            "morae": [],
            "feedback": [],
            "recognizer": recognizer_metadata,
        }

    student_mfcc = student_features["mfcc"]
    reference_mfcc = reference_features["mfcc"]
    alignment_path = _dtw_alignment_path(student_mfcc, reference_mfcc)
    reference_ranges = _weighted_frame_ranges(
        phoneme_targets,
        _frame_count(reference_mfcc),
    )

    phone_details: list[dict[str, Any]] = []
    for phone, reference_range in zip(phoneme_targets, reference_ranges, strict=False):
        student_range = _student_range_for_reference_range(
            alignment_path,
            reference_range,
            student_frame_count=_frame_count(student_mfcc),
            reference_frame_count=_frame_count(reference_mfcc),
        )
        detail = _score_phoneme(
            phone=phone,
            student_features=student_features,
            reference_features=reference_features,
            student_range=student_range,
            reference_range=reference_range,
        )
        phone_details.append(detail)

    recognition, ctc_warning = _run_ctc_recognition(student_audio)
    if recognition is not None:
        phone_details = _apply_ctc_alignment(
            phone_details=phone_details,
            recognition=recognition,
        )
        recognizer_metadata = _recognizer_metadata(recognition=recognition)
    elif _uses_hf_ctc_provider():
        recognizer_metadata = _recognizer_metadata(
            warning=ctc_warning
            or "HF CTC recognizer was unavailable; used reference-aligned acoustic scoring.",
            fallback_used=True,
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

    phoneme_match_score = _weighted_average(
        [item["score"] for item in phone_details],
        [float(item.get("weight", 1.0)) for item in phone_details],
        fallback=overall_acoustic_score,
    )
    mora_timing_score = _average(
        [item["duration_score"] for item in mora_details],
        fallback=_duration_score(
            student_features.get("duration", 0.0),
            reference_features.get("duration", 0.0),
        ),
    )
    consonant_score = _average(
        [
            item["score"]
            for item in phone_details
            if item["type"] in {"consonant", "glide", "nasal", "pause"}
        ],
        fallback=overall_acoustic_score,
    )
    vowel_score = _average(
        [item["score"] for item in phone_details if item["type"] == "vowel"],
        fallback=overall_acoustic_score,
    )

    return {
        "target_pronunciation": enriched_target,
        "phoneme_match_score": round(phoneme_match_score, 2),
        "mora_timing_score": round(mora_timing_score, 2),
        "consonant_score": round(consonant_score, 2),
        "vowel_score": round(vowel_score, 2),
        "fluency_score": _fluency_score(student_features, reference_features),
        "phonemes": phone_details,
        "morae": mora_details,
        "feedback": feedback,
        "recognizer": recognizer_metadata,
    }


def _apply_rule_issue_types(
    target_pronunciation: dict[str, Any],
    pronunciation_rules: list[Any],
) -> dict[str, Any]:
    rules_by_chunk = {
        int(getattr(rule, "chunk_index", index)): str(getattr(rule, "issue_type", ""))
        for index, rule in enumerate(pronunciation_rules)
    }
    payload = dict(target_pronunciation)
    phonemes: list[dict[str, Any]] = []
    for phone in payload.get("phonemes", []):
        updated = dict(phone)
        rule_issue = rules_by_chunk.get(int(updated.get("chunk_index", 0)))
        if _rule_applies_to_phone(rule_issue, updated):
            updated["issue_type"] = rule_issue
        phonemes.append(updated)

    morae: list[dict[str, Any]] = []
    for mora in payload.get("morae", []):
        updated = dict(mora)
        rule_issue = rules_by_chunk.get(int(updated.get("chunk_index", 0)))
        if rule_issue:
            updated["issue_type"] = rule_issue
        morae.append(updated)

    payload["phonemes"] = phonemes
    payload["morae"] = morae
    return payload


def _rule_applies_to_phone(rule_issue: str | None, phone: dict[str, Any]) -> bool:
    if not rule_issue:
        return False

    symbol = str(phone.get("symbol", ""))
    phone_type = str(phone.get("type", ""))
    if rule_issue == R_SOUND_ISSUE:
        return symbol.startswith("r")
    if rule_issue in {LONG_VOWEL_ISSUE, DEVOICING_ISSUE}:
        return phone_type == "vowel"
    return True


def _run_ctc_recognition(student_audio: bytes | None) -> tuple[Any | None, str | None]:
    if not _uses_hf_ctc_provider() or student_audio is None:
        return None, None

    try:
        from app.services.hf_phoneme_recognizer import recognize_pronunciation_audio

        recognition = recognize_pronunciation_audio(student_audio)
        if not recognition.recognized_phonemes:
            raise RuntimeError("HF CTC recognizer returned no phonemes")
        return recognition, None
    except Exception as error:
        if not settings.PHONEME_CTC_FALLBACK_ENABLED:
            raise RuntimeError(f"HF CTC phoneme recognition failed: {error}") from error
        logger.warning("HF CTC phoneme recognition fallback: %s", error)
        return (
            None,
            "HF CTC recognizer was unavailable; used reference-aligned acoustic scoring. "
            f"Reason: {error}",
        )


def _uses_hf_ctc_provider() -> bool:
    return settings.PHONEME_ASSESSMENT_PROVIDER.strip().lower() in {
        "hybrid_hf_ctc",
        "hf_ctc",
    }


def _apply_ctc_alignment(
    *,
    phone_details: list[dict[str, Any]],
    recognition: Any,
) -> list[dict[str, Any]]:
    expected = [str(item.get("expected_phoneme", "")) for item in phone_details]
    spoken = [str(item) for item in recognition.recognized_phonemes]
    alignment = align_phoneme_sequences(expected, spoken)
    confidence_by_spoken_index = {
        int(item.get("position", index)): float(item.get("confidence", recognition.confidence))
        for index, item in enumerate(getattr(recognition, "token_confidences", []))
    }

    updated_by_expected: dict[int, dict[str, Any]] = {
        int(item["index"]): dict(item) for item in phone_details
    }
    inserted: list[dict[str, Any]] = []

    for item in alignment:
        operation = str(item["operation"])
        expected_index = item.get("expected_index")
        spoken_index = item.get("spoken_index")
        confidence = confidence_by_spoken_index.get(
            int(spoken_index) if spoken_index is not None else -1,
            float(getattr(recognition, "confidence", 0.0)),
        )

        if expected_index is None:
            inserted.append(
                _build_inserted_phone_detail(
                    alignment_item=item,
                    phone_details=phone_details,
                    confidence=confidence,
                )
            )
            continue

        expected_index = int(expected_index)
        detail = updated_by_expected.get(expected_index)
        if detail is None:
            continue

        operation = _relax_ctc_operation(detail, operation, item)
        ctc_score = _ctc_operation_score(operation, confidence)
        acoustic_score = float(detail.get("score", 0.0))
        combined_score = (ctc_score * 0.70) + (acoustic_score * 0.30)
        if operation == "match" and detail.get("operation") == "duration_error":
            operation = "duration_error"
            combined_score = min(combined_score, float(detail.get("duration_score", combined_score)))

        heard_phoneme = str(item.get("heard_phoneme", "unclear"))
        detail["operation"] = operation
        detail["heard_phoneme"] = heard_phoneme
        detail["heard_label"] = _heard_label_for_ctc(heard_phoneme, operation)
        detail["score"] = round(max(0.0, min(combined_score, 100.0)), 2)
        detail["error"] = detail["score"] < 78.0 or operation not in {"match"}
        detail["issue_type"] = _ctc_issue_type(detail, operation)
        detail["ctc_confidence"] = round(confidence, 4)
        updated_by_expected[expected_index] = detail

    updated = [updated_by_expected[int(item["index"])] for item in phone_details]
    updated.extend(inserted)
    updated.sort(key=lambda item: (int(item.get("mora_index", 0)), int(item.get("index", 0))))
    return updated


def _phonemes_equivalent(expected: str, spoken: str) -> bool:
    if expected == spoken:
        return True
    if expected == "N" and spoken in {"n", "m", "ng"}:
        return True
    return False


def _relax_ctc_operation(
    detail: dict[str, Any],
    operation: str,
    alignment_item: dict[str, Any],
) -> str:
    if operation == "match":
        return operation

    expected = str(detail.get("expected_phoneme", ""))
    heard = str(alignment_item.get("heard_phoneme", ""))
    target_issue = str(detail.get("target_issue_type", ""))
    kana = str(detail.get("kana", ""))
    romaji = str(detail.get("romaji", ""))

    if expected == "N" and heard in {"n", "m", "ng"}:
        return "match"

    # The HF CTC model often omits the light /w/ glide in sentence-final
    # particle は even when the vowel is correctly spoken as "wa". Do not turn
    # that recognizer artifact into learner feedback; literal "ha" remains an
    # error because heard "h" is not relaxed here.
    if (
        target_issue == "particle_pronunciation"
        and kana == "\u306f"
        and romaji == "wa"
        and expected == "w"
        and operation == "deletion"
    ):
        return "match"

    return operation


def _build_inserted_phone_detail(
    *,
    alignment_item: dict[str, Any],
    phone_details: list[dict[str, Any]],
    confidence: float,
) -> dict[str, Any]:
    spoken_index = alignment_item.get("spoken_index")
    expected_neighbors = [
        phone for phone in phone_details if int(phone.get("index", 0)) <= int(spoken_index or 0)
    ]
    anchor = expected_neighbors[-1] if expected_neighbors else (phone_details[0] if phone_details else {})
    heard_phoneme = str(alignment_item.get("heard_phoneme", "unclear"))

    return {
        "index": len(phone_details) + int(spoken_index or 0),
        "mora_index": int(anchor.get("mora_index", 0)),
        "chunk_index": int(anchor.get("chunk_index", 0)),
        "kana": str(anchor.get("kana", "")),
        "romaji": str(anchor.get("romaji", "")),
        "expected_phoneme": None,
        "expected_label": "No extra sound expected",
        "heard_phoneme": heard_phoneme,
        "heard_label": _heard_label_for_ctc(heard_phoneme, "insertion"),
        "type": "consonant",
        "issue_type": "insertion",
        "operation": "insertion",
        "score": round(_ctc_operation_score("insertion", confidence), 2),
        "error": True,
        "weight": 0.55,
        "duration_score": 70.0,
        "student_duration_ms": 0.0,
        "reference_duration_ms": 0.0,
        "reference_frame_start": int(anchor.get("reference_frame_start", 0)),
        "reference_frame_end": int(anchor.get("reference_frame_end", 0)),
        "student_frame_start": int(anchor.get("student_frame_start", 0)),
        "student_frame_end": int(anchor.get("student_frame_end", 0)),
        "ctc_confidence": round(confidence, 4),
    }


def _ctc_operation_score(operation: str, confidence: float) -> float:
    confidence = max(0.0, min(float(confidence), 1.0))
    if operation == "match":
        return 84.0 + (confidence * 16.0)
    if operation == "substitution":
        return 48.0 - (confidence * 12.0)
    if operation == "insertion":
        return 42.0 - (confidence * 10.0)
    if operation == "deletion":
        return 22.0
    return 58.0


def _heard_label_for_ctc(phoneme: str, operation: str) -> str:
    if operation == "deletion":
        return "omitted or clipped"
    if operation == "insertion":
        return f"extra {phoneme} sound"
    if phoneme == "unclear":
        return "unclear sound"
    return _phoneme_label(phoneme, "vowel" if phoneme in VOWELS else "consonant")


def _ctc_issue_type(detail: dict[str, Any], operation: str) -> str:
    if operation == "match":
        return "match"
    if operation in {"substitution", "deletion", "insertion"}:
        original_issue = str(detail.get("issue_type", ""))
        target_issue = str(detail.get("target_issue_type", ""))
        expected_phoneme = str(detail.get("expected_phoneme", ""))
        if target_issue == GEMINATE_ISSUE or expected_phoneme == "Q":
            return "geminate_issue"
        if target_issue == NASAL_ISSUE or expected_phoneme == "N":
            return "nasal_issue"
        if target_issue == LONG_VOWEL_ISSUE:
            return "long_vowel_issue"
        if original_issue in {
            "long_vowel_issue",
            "geminate_issue",
            "nasal_issue",
            "r_flap_issue",
            "devoicing_issue",
        }:
            return original_issue
        if str(detail.get("expected_phoneme", "")).startswith("r"):
            return "r_flap_issue"
        if str(detail.get("type")) == "vowel":
            return "vowel_drift"
        return operation
    return str(detail.get("issue_type", operation))


def _score_phoneme(
    *,
    phone: dict[str, Any],
    student_features: dict[str, Any],
    reference_features: dict[str, Any],
    student_range: tuple[int, int],
    reference_range: tuple[int, int],
) -> dict[str, Any]:
    student_slice = _mfcc_slice(student_features["mfcc"], student_range)
    reference_slice = _mfcc_slice(reference_features["mfcc"], reference_range)
    phone_type = str(phone.get("type", "consonant"))
    issue_type = str(phone.get("issue_type", CONSONANT_ISSUE))

    if phone_type == "vowel":
        base_score = _slice_score(student_slice[1:6, :], reference_slice[1:6, :])
    elif phone_type in {"consonant", "glide"}:
        base_score = _slice_score(student_slice[6:, :], reference_slice[6:, :])
    else:
        base_score = _slice_score(student_slice, reference_slice)

    student_duration = _range_duration(student_features, student_range)
    reference_duration = _range_duration(reference_features, reference_range)
    duration_score = _duration_score(student_duration, reference_duration)
    student_rms = _waveform_rms(student_features, student_range)
    reference_rms = _waveform_rms(reference_features, reference_range)
    adjusted_score = _apply_issue_penalties(
        base_score=base_score,
        issue_type=issue_type,
        phone_type=phone_type,
        student_duration=student_duration,
        reference_duration=reference_duration,
        duration_score=duration_score,
        student_rms=student_rms,
        reference_rms=reference_rms,
    )
    operation = _alignment_operation(
        issue_type=issue_type,
        score=adjusted_score,
        student_duration=student_duration,
        reference_duration=reference_duration,
    )
    heard_phoneme, heard_label = _heard_sound(
        expected=str(phone.get("symbol", "")),
        label=str(phone.get("label", "")),
        score=adjusted_score,
        operation=operation,
    )

    return {
        "index": int(phone.get("index", 0)),
        "mora_index": int(phone.get("mora_index", 0)),
        "chunk_index": int(phone.get("chunk_index", 0)),
        "kana": str(phone.get("kana", "")),
        "romaji": str(phone.get("romaji", "")),
        "expected_phoneme": str(phone.get("symbol", "")),
        "expected_label": str(phone.get("label", "")),
        "heard_phoneme": heard_phoneme,
        "heard_label": heard_label,
        "type": phone_type,
        "target_issue_type": issue_type,
        "issue_type": _detail_issue_type(
            phone_type=phone_type,
            issue_type=issue_type,
            score=adjusted_score,
            operation=operation,
        ),
        "operation": operation,
        "score": round(adjusted_score, 2),
        "error": adjusted_score < 78.0,
        "weight": float(phone.get("weight", 1.0)),
        "duration_score": round(duration_score, 2),
        "student_duration_ms": round(student_duration * 1000.0, 1),
        "reference_duration_ms": round(reference_duration * 1000.0, 1),
        "reference_frame_start": reference_range[0],
        "reference_frame_end": reference_range[1],
        "student_frame_start": student_range[0],
        "student_frame_end": student_range[1],
    }


def _score_morae(
    *,
    mora_targets: list[dict[str, Any]],
    phone_details: list[dict[str, Any]],
    pronunciation_rules: list[Any],
) -> list[dict[str, Any]]:
    rules_by_chunk = {
        int(getattr(rule, "chunk_index", index)): rule
        for index, rule in enumerate(pronunciation_rules)
    }
    phones_by_mora: dict[int, list[dict[str, Any]]] = {}
    for phone in phone_details:
        phones_by_mora.setdefault(int(phone["mora_index"]), []).append(phone)

    details: list[dict[str, Any]] = []
    for mora in mora_targets:
        mora_index = int(mora.get("index", 0))
        chunk_index = int(mora.get("chunk_index", mora_index))
        phones = phones_by_mora.get(mora_index, [])
        rule = rules_by_chunk.get(chunk_index)
        issue_type = str(getattr(rule, "issue_type", mora.get("issue_type", CONSONANT_ISSUE)))
        phone_score = _weighted_average(
            [phone["score"] for phone in phones],
            [float(phone.get("weight", 1.0)) for phone in phones],
            fallback=100.0,
        )
        duration_score = _average(
            [phone["duration_score"] for phone in phones],
            fallback=phone_score,
        )
        weakest_phone_score = min(
            [float(phone["score"]) for phone in phones],
            default=phone_score,
        )
        score = (phone_score * 0.55) + (weakest_phone_score * 0.25) + (duration_score * 0.20)
        threshold = float(getattr(rule, "threshold", 80.0))

        details.append(
            {
                "index": mora_index,
                "chunk_index": chunk_index,
                "display_text": str(mora.get("display_text", mora.get("kana", ""))),
                "kana": str(mora.get("kana", "")),
                "romaji": str(mora.get("romaji", "")),
                "phoneme_indexes": list(mora.get("phoneme_indexes", [])),
                "expected_phonemes": [
                    phone["expected_phoneme"]
                    for phone in phones
                    if phone.get("expected_phoneme") is not None
                ],
                "heard_phonemes": [
                    phone["heard_phoneme"]
                    for phone in phones
                    if phone.get("heard_phoneme") is not None
                ],
                "issue_type": issue_type,
                "score": round(score, 2),
                "duration_score": round(duration_score, 2),
                "error": score < threshold,
                "threshold": threshold,
                "fix_tip": str(
                    getattr(
                        rule,
                        "fix_tip",
                        "Replay the model audio and match this sound more closely.",
                    )
                ),
            }
        )

    return details


def _build_feedback(
    *,
    mora_details: list[dict[str, Any]],
    phone_details: list[dict[str, Any]],
    pronunciation_rules: list[Any],
) -> list[dict[str, Any]]:
    rules_by_chunk = {
        int(getattr(rule, "chunk_index", index)): rule
        for index, rule in enumerate(pronunciation_rules)
    }
    phones_by_mora: dict[int, list[dict[str, Any]]] = {}
    for phone in phone_details:
        phones_by_mora.setdefault(int(phone["mora_index"]), []).append(phone)

    feedback: list[dict[str, Any]] = []
    slow_practice_text = _slow_practice_text(mora_details)
    for mora in mora_details:
        if not bool(mora["error"]):
            continue

        chunk_index = int(mora["chunk_index"])
        rule = rules_by_chunk.get(chunk_index)
        phones = phones_by_mora.get(int(mora["index"]), [])
        focus_phone = _focus_phone_for_issue(str(mora["issue_type"]), phones)
        issue_type = str(mora["issue_type"])
        score = min(float(mora["score"]), float(focus_phone.get("score", mora["score"])))

        simple_guidance = _student_guidance(
            issue_type=issue_type,
            mora=mora,
            focus_phone=focus_phone,
            slow_practice_text=slow_practice_text,
        )
        feedback.append(
            {
                "chunk_index": chunk_index,
                "mora_index": int(mora["index"]),
                "phoneme_index": int(focus_phone.get("index", 0)),
                "display_text": str(mora["display_text"]),
                "kana": str(mora["kana"]),
                "romaji": str(mora["romaji"]),
                "expected_phoneme": _optional_text(focus_phone.get("expected_phoneme")),
                "expected_label": str(focus_phone.get("expected_label", "")),
                "heard_phoneme": _optional_text(focus_phone.get("heard_phoneme")),
                "heard_label": str(focus_phone.get("heard_label", "")),
                "issue_type": issue_type,
                "severity": _severity_label(score),
                "score": round(score, 2),
                "expected_note": str(
                    getattr(
                        rule,
                        "expected_note",
                        _expected_note(issue_type, focus_phone),
                    )
                ),
                "heard_note": _heard_note(issue_type, focus_phone),
                "fix_tip": str(
                    getattr(
                        rule,
                        "fix_tip",
                        _fix_tip(issue_type, focus_phone),
                    )
                ),
                "sound_to_improve": simple_guidance["sound_to_improve"],
                "what_happened": simple_guidance["what_happened"],
                "how_to_fix": simple_guidance["how_to_fix"],
                "try_slowly": simple_guidance["try_slowly"],
            }
        )

    feedback.sort(key=lambda item: (_issue_priority(item["issue_type"]), item["score"]))
    return feedback


def _slow_practice_text(mora_details: list[dict[str, Any]]) -> str:
    kana = [str(item.get("kana", "")).strip() for item in mora_details]
    return "\u30fb".join(item for item in kana if item)


def _student_guidance(
    *,
    issue_type: str,
    mora: dict[str, Any],
    focus_phone: dict[str, Any],
    slow_practice_text: str,
) -> dict[str, str]:
    sound = str(mora.get("kana") or focus_phone.get("expected_phoneme") or "this sound")
    expected = str(focus_phone.get("expected_phoneme") or sound)
    heard = str(focus_phone.get("heard_phoneme") or "unclear")

    guidance_by_issue = {
        LONG_VOWEL_ISSUE: (
            "It sounded too short.",
            "Hold this vowel one beat longer before moving to the next sound.",
        ),
        GEMINATE_ISSUE: (
            "The small pause was missing or too weak.",
            "Pause for a tiny beat, then release the next consonant clearly.",
        ),
        NASAL_ISSUE: (
            "The nasal sound was too short or unclear.",
            "Make \u3093 a full beat. Do not add an extra vowel after it.",
        ),
        R_SOUND_ISSUE: (
            "The Japanese R did not sound light enough.",
            "Tap your tongue lightly behind the teeth, between L and D.",
        ),
        DEVOICING_ISSUE: (
            "The ending sounded too strong.",
            "Make the final vowel softer and lighter.",
        ),
        "particle_pronunciation": (
            "This particle sounded closer to the written kana.",
            "Use the spoken particle sound here, like wa for final \u306f.",
        ),
        "contracted_sound": (
            "The blended sound was separated too much.",
            "Say the small-y sound smoothly in one beat.",
        ),
    }
    what_happened, how_to_fix = guidance_by_issue.get(
        issue_type,
        (
            f"We heard {heard} instead of a clear {expected}.",
            _fix_tip(issue_type, focus_phone),
        ),
    )

    if issue_type == "vowel_quality" or str(focus_phone.get("type")) == "vowel":
        what_happened = "The vowel moved or changed shape."
        how_to_fix = f"Keep the {expected} vowel steady and clean."
    elif issue_type == "insertion":
        what_happened = "There was an extra sound."
        how_to_fix = "End the sound cleanly without adding another vowel."

    return {
        "sound_to_improve": sound,
        "what_happened": what_happened,
        "how_to_fix": how_to_fix,
        "try_slowly": slow_practice_text or sound,
    }


def _phone_specs_for_mora(
    kana: str,
    romaji: str,
    mora_issue: str,
) -> list[PhoneSpec]:
    normalized = _normalize_romaji(romaji)
    if kana == PAUSE_KANA or normalized in {"pause", "xtsu", "ltsu", "q"}:
        return [PhoneSpec("Q", "pause", GEMINATE_ISSUE, 0.85)]

    if kana == NASAL_KANA or normalized in {"n", "nn", "n'"}:
        return [PhoneSpec("N", "nasal", NASAL_ISSUE, 0.85)]

    normalized = normalized.replace("'", "")
    if normalized == "wo":
        normalized = "o"

    vowel = _final_vowel(normalized)
    onset = normalized[: -len(vowel)] if vowel else normalized
    specs: list[PhoneSpec] = []

    if onset:
        onset_symbol, onset_kind = _normalize_onset(onset)
        specs.append(
            PhoneSpec(
                onset_symbol,
                onset_kind,
                R_SOUND_ISSUE if onset_symbol.startswith("r") else CONSONANT_ISSUE,
                _phone_weight(onset_kind, onset_symbol),
            )
        )

    if vowel:
        specs.append(
            PhoneSpec(
                vowel,
                "vowel",
                LONG_VOWEL_ISSUE if mora_issue == LONG_VOWEL_ISSUE else VOWEL_ISSUE,
                1.25 if mora_issue == LONG_VOWEL_ISSUE else 1.0,
            )
        )

    if not specs and normalized:
        specs.append(PhoneSpec(normalized, "consonant", CONSONANT_ISSUE, 0.65))

    return specs


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _normalize_onset(onset: str) -> tuple[str, str]:
    if onset in PALATALIZED_ONSETS:
        return onset, "consonant"

    for special in SPECIAL_ONSETS:
        if onset == special:
            return special, "consonant"

    if len(onset) == 2 and onset[1] == "y":
        return onset, "consonant"

    if onset == "y" or onset == "w":
        return onset, "glide"

    return onset, "consonant"


def _mora_issue_type(kana: str, romaji: str, previous_vowel: str) -> str:
    if kana == PAUSE_KANA or romaji == "pause":
        return GEMINATE_ISSUE
    if kana == NASAL_KANA:
        return NASAL_ISSUE
    if _is_long_vowel_mora(kana, romaji, previous_vowel):
        return LONG_VOWEL_ISSUE
    if any(marker in kana for marker in SMALL_Y_KANA):
        return "contracted_sound"
    if romaji.startswith("r"):
        return R_SOUND_ISSUE
    if _final_vowel(romaji):
        return VOWEL_ISSUE if not _normalize_romaji(romaji)[:-1] else CONSONANT_ISSUE
    return CONSONANT_ISSUE


def _is_long_vowel_mora(kana: str, romaji: str, previous_vowel: str) -> bool:
    current_vowel = _final_vowel(romaji)
    if not current_vowel or not previous_vowel:
        return LONG_MARK in kana

    if LONG_MARK in kana:
        return True
    if current_vowel == previous_vowel:
        return True
    if kana == LONG_O_KANA and previous_vowel in {"o", "u"}:
        return True
    if kana == LONG_I_KANA and previous_vowel in {"e", "i"}:
        return True
    return False


def _final_vowel_from_specs(specs: list[PhoneSpec]) -> str:
    for spec in reversed(specs):
        if spec.kind == "vowel":
            return spec.symbol
    return ""


def _final_vowel(romaji: str) -> str:
    normalized = _normalize_romaji(romaji)
    for char in reversed(normalized):
        if char in VOWELS:
            return char
    return ""


def _normalize_romaji(value: str) -> str:
    return "".join(str(value).lower().strip().split())


def _phoneme_label(symbol: str, kind: str) -> str:
    if symbol in VOWELS:
        return f"{symbol} vowel"
    if symbol == "Q":
        return "small-tsu hold"
    if symbol == "N":
        return "mora nasal"
    if symbol == "r":
        return "Japanese r-flap"
    if kind == "glide":
        return f"{symbol} glide"
    return f"{symbol} consonant"


def _phone_weight(kind: str, symbol: str) -> float:
    if kind == "vowel":
        return 1.0
    if kind == "glide":
        return 0.35
    if kind == "nasal":
        return 0.85
    if kind == "pause":
        return 0.85
    if symbol in {"sh", "ch", "ts", "ky", "gy", "ny", "hy", "by", "py", "my", "ry"}:
        return 0.75
    return 0.65


def _dtw_alignment_path(seq_a: np.ndarray, seq_b: np.ndarray) -> list[tuple[int, int]]:
    if seq_a.size == 0 or seq_b.size == 0:
        return [(0, 0)]

    a = _normalize_feature_sequence(seq_a).T
    b = _normalize_feature_sequence(seq_b).T
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

    i = t1 - 1
    j = t2 - 1
    path = [(i, j)]
    while i > 0 or j > 0:
        candidates: list[tuple[float, int, int]] = []
        if i > 0 and j > 0:
            candidates.append((float(accumulated[i - 1, j - 1]), i - 1, j - 1))
        if i > 0:
            candidates.append((float(accumulated[i - 1, j]), i - 1, j))
        if j > 0:
            candidates.append((float(accumulated[i, j - 1]), i, j - 1))
        _, i, j = min(candidates, key=lambda item: item[0])
        path.append((i, j))

    path.reverse()
    return path


def _normalize_feature_sequence(seq: np.ndarray) -> np.ndarray:
    mean_value = np.mean(seq, axis=1, keepdims=True)
    std = np.std(seq, axis=1, keepdims=True)
    return (seq - mean_value) / np.maximum(std, 1e-6)


def _weighted_frame_ranges(
    phonemes: list[dict[str, Any]],
    frame_count: int,
) -> list[tuple[int, int]]:
    if frame_count <= 0:
        return [(0, 1) for _ in phonemes]

    weights = [max(0.1, float(phone.get("weight", 1.0))) for phone in phonemes]
    total = sum(weights) or 1.0
    ranges: list[tuple[int, int]] = []
    cursor = 0
    cumulative = 0.0

    for index, weight in enumerate(weights):
        cumulative += weight
        if index == len(weights) - 1:
            end = frame_count
        else:
            end = int(round((cumulative / total) * frame_count))
        end = min(max(end, cursor + 1), frame_count)
        start = min(cursor, max(0, frame_count - 1))
        ranges.append((start, max(end, start + 1)))
        cursor = end

    return ranges


def _student_range_for_reference_range(
    alignment_path: list[tuple[int, int]],
    reference_range: tuple[int, int],
    *,
    student_frame_count: int,
    reference_frame_count: int,
) -> tuple[int, int]:
    start, end = reference_range
    matched = [student for student, ref in alignment_path if start <= ref < end]
    if matched:
        return (max(0, min(matched)), min(student_frame_count, max(matched) + 1))

    ratio = student_frame_count / max(reference_frame_count, 1)
    fallback_start = int(round(start * ratio))
    fallback_end = int(round(end * ratio))
    fallback_start = min(max(0, fallback_start), max(0, student_frame_count - 1))
    fallback_end = min(max(fallback_start + 1, fallback_end), student_frame_count)
    return (fallback_start, fallback_end)


def _mfcc_slice(mfcc: np.ndarray, frame_range: tuple[int, int]) -> np.ndarray:
    start, end = frame_range
    frame_count = _frame_count(mfcc)
    start = min(max(0, start), max(0, frame_count - 1))
    end = min(max(start + 1, end), frame_count)
    return mfcc[:, start:end]


def _slice_score(student_slice: np.ndarray, reference_slice: np.ndarray) -> float:
    if student_slice.size == 0 or reference_slice.size == 0:
        return 0.0
    if student_slice.shape[1] < 2 or reference_slice.shape[1] < 2:
        return 100.0 if student_slice.shape == reference_slice.shape else 70.0

    a = _normalize_feature_sequence(student_slice).T
    b = _normalize_feature_sequence(reference_slice).T
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

    return _dtw_to_score(float(accumulated[t1 - 1, t2 - 1] / (t1 + t2)))


def _dtw_to_score(dtw_dist: float) -> float:
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
            return round(previous_score + ((threshold_score - previous_score) * ratio), 2)
        previous_dist = threshold_dist
        previous_score = threshold_score

    if dtw_dist >= 1.6:
        return 0.0
    tail_ratio = (dtw_dist - 1.25) / 0.35
    return round(max(0.0, 15.0 * (1.0 - tail_ratio)), 2)


def _apply_issue_penalties(
    *,
    base_score: float,
    issue_type: str,
    phone_type: str,
    student_duration: float,
    reference_duration: float,
    duration_score: float,
    student_rms: float,
    reference_rms: float,
) -> float:
    score = base_score
    duration_ratio = student_duration / max(reference_duration, 1e-4)
    energy_ratio = student_rms / max(reference_rms, 1e-4)

    if issue_type == LONG_VOWEL_ISSUE and duration_ratio < 0.82:
        score = min(score, duration_score)
        score = max(0.0, score - ((0.82 - duration_ratio) * 45.0))
    elif issue_type == GEMINATE_ISSUE:
        if duration_ratio < 0.72:
            score = max(0.0, min(score, duration_score) - ((0.72 - duration_ratio) * 42.0))
        if energy_ratio > 1.35:
            score = max(0.0, score - ((energy_ratio - 1.35) * 24.0))
    elif issue_type == NASAL_ISSUE and duration_ratio < 0.72:
        score = max(0.0, min(score, duration_score) - ((0.72 - duration_ratio) * 30.0))
    elif issue_type == DEVOICING_ISSUE and energy_ratio > 1.35:
        score = max(0.0, score - ((energy_ratio - 1.35) * 28.0))
    elif phone_type == "vowel" and duration_score < 70.0:
        score = (score * 0.75) + (duration_score * 0.25)

    return round(max(0.0, min(score, 100.0)), 2)


def _duration_score(student_duration: float, reference_duration: float) -> float:
    if reference_duration <= 0:
        return 100.0
    ratio = student_duration / reference_duration
    deviation = abs(1.0 - ratio)
    if deviation <= 0.15:
        return 100.0
    if deviation >= 0.60:
        return 0.0
    return round(max(0.0, 100.0 * (1.0 - ((deviation - 0.15) / 0.45))), 2)


def _fluency_score(
    student_features: dict[str, Any],
    reference_features: dict[str, Any],
) -> float:
    duration = _duration_score(
        float(student_features.get("duration", 0.0)),
        float(reference_features.get("duration", 0.0)),
    )
    voiced_ratio = float(student_features.get("voiced_ratio", 0.0))
    reference_voiced_ratio = float(reference_features.get("voiced_ratio", voiced_ratio))
    if reference_voiced_ratio <= 0:
        density = 100.0
    else:
        density = _duration_score(voiced_ratio, reference_voiced_ratio)
    return round((duration * 0.62) + (density * 0.38), 2)


def _alignment_operation(
    *,
    issue_type: str,
    score: float,
    student_duration: float,
    reference_duration: float,
) -> str:
    duration_ratio = student_duration / max(reference_duration, 1e-4)
    if score < 45.0 and duration_ratio < 0.58:
        return "deletion"
    if issue_type in {LONG_VOWEL_ISSUE, GEMINATE_ISSUE, NASAL_ISSUE} and score < 78.0:
        return "duration_error"
    if score < 78.0:
        return "substitution"
    return "match"


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


def _focus_phone_for_issue(
    issue_type: str,
    phones: list[dict[str, Any]],
) -> dict[str, Any]:
    if not phones:
        return {}

    if issue_type == R_SOUND_ISSUE:
        for phone in phones:
            if str(phone.get("expected_phoneme", "")).startswith("r"):
                return phone

    if issue_type == LONG_VOWEL_ISSUE:
        vowel_phones = [phone for phone in phones if phone.get("type") == "vowel"]
        if vowel_phones:
            return min(vowel_phones, key=lambda item: item["score"])

    return min(phones, key=lambda item: item["score"])


def _expected_note(issue_type: str, phone: dict[str, Any]) -> str:
    expected = str(phone.get("expected_label", phone.get("expected_phoneme", "this sound")))
    if issue_type == LONG_VOWEL_ISSUE:
        return f"{expected} should be held for the full long-vowel beat."
    if issue_type == GEMINATE_ISSUE:
        return "Small tsu should sound like a brief held beat before the next consonant."
    if issue_type == NASAL_ISSUE:
        return "The mora nasal should stay distinct without an extra vowel after it."
    if issue_type == R_SOUND_ISSUE:
        return "Japanese r should stay light and tapped, not like a heavy English r."
    if issue_type == DEVOICING_ISSUE:
        return "This ending is often softened in natural Japanese speech."
    return f"Target {expected} should stay clear and steady."


def _heard_note(issue_type: str, phone: dict[str, Any]) -> str:
    heard = str(phone.get("heard_label", "an unclear sound"))
    score = float(phone.get("score", 0.0))
    if issue_type == LONG_VOWEL_ISSUE:
        return "The long vowel sounded clipped or too short."
    if issue_type == GEMINATE_ISSUE:
        return "The held beat before the next consonant was not distinct enough."
    if issue_type == NASAL_ISSUE:
        return "The nasal mora blended into the surrounding sounds."
    if issue_type == R_SOUND_ISSUE:
        return "The r-flap did not match the light Japanese tap closely enough."
    if issue_type == DEVOICING_ISSUE:
        return "The ending sounded stronger than the softer target."
    if score < 62.0:
        return f"We heard {heard} instead of a clean target sound."
    return f"We heard {heard}; it is close but still unstable."


def _fix_tip(issue_type: str, phone: dict[str, Any]) -> str:
    expected = str(phone.get("expected_phoneme", "the target sound"))
    if issue_type == LONG_VOWEL_ISSUE:
        return "Hold the vowel for one extra mora before moving on."
    if issue_type == GEMINATE_ISSUE:
        return "Hold a tiny silent beat, then release the next consonant crisply."
    if issue_type == NASAL_ISSUE:
        return "Close into the nasal sound cleanly without adding a trailing vowel."
    if issue_type == R_SOUND_ISSUE:
        return "Tap the tongue lightly behind the teeth for the Japanese r-flap."
    if issue_type == DEVOICING_ISSUE:
        return "Lighten the final vowel so it does not become too fully voiced."
    if str(phone.get("type")) == "vowel":
        return f"Keep the {expected} vowel steady without sliding."
    return f"Replay the model and make the {expected} sound crisper."


def _severity_label(score: float) -> str:
    if score < 55:
        return "high"
    if score < 75:
        return "medium"
    return "low"


def _issue_priority(issue_type: str) -> int:
    priorities = {
        GEMINATE_ISSUE: 0,
        LONG_VOWEL_ISSUE: 1,
        NASAL_ISSUE: 2,
        R_SOUND_ISSUE: 3,
        DEVOICING_ISSUE: 4,
    }
    return priorities.get(issue_type, 5)


def _frame_count(mfcc: np.ndarray) -> int:
    return int(mfcc.shape[1]) if mfcc.ndim == 2 else 0


def _range_duration(features: dict[str, Any], frame_range: tuple[int, int]) -> float:
    frame_count = _frame_count(features["mfcc"])
    if frame_count <= 0:
        return 0.0
    start, end = frame_range
    frame_span = max(1, end - start)
    return float(features.get("duration", 0.0)) * (frame_span / frame_count)


def _waveform_rms(features: dict[str, Any], frame_range: tuple[int, int]) -> float:
    waveform = features.get("waveform")
    if waveform is None or waveform.size == 0:
        return 0.0
    frame_count = _frame_count(features["mfcc"])
    if frame_count <= 0:
        return 0.0
    start, end = frame_range
    sample_start = int(round((start / frame_count) * waveform.shape[0]))
    sample_end = int(round((end / frame_count) * waveform.shape[0]))
    sample_start = min(max(0, sample_start), max(0, waveform.shape[0] - 1))
    sample_end = min(max(sample_start + 1, sample_end), waveform.shape[0])
    segment = waveform[sample_start:sample_end]
    return float(np.sqrt(np.mean(np.square(segment)))) if segment.size else 0.0


def _average(values: list[float], *, fallback: float) -> float:
    return float(mean(values)) if values else float(fallback)


def _weighted_average(
    values: list[float],
    weights: list[float],
    *,
    fallback: float,
) -> float:
    if not values:
        return float(fallback)
    total_weight = sum(weights) or 1.0
    return float(sum(value * weight for value, weight in zip(values, weights, strict=False)) / total_weight)


def _recognizer_metadata(
    *,
    recognition: Any | None = None,
    warning: str | None = None,
    fallback_used: bool = False,
) -> dict[str, Any]:
    if recognition is not None:
        return recognition.to_metadata()

    if _uses_hf_ctc_provider():
        return {
            "provider": "hybrid_hf_ctc",
            "ctc_model_id": settings.PHONEME_CTC_MODEL_ID,
            "ctc_enabled": False,
            "fallback_used": fallback_used,
            "warning": warning,
            "note": "HF CTC phoneme recognition was requested; reference-aligned timing/acoustic scoring is carrying this result.",
        }

    return {
        "provider": "reference_aligned_phoneme_dtw",
        "ctc_model_id": settings.PHONEME_CTC_MODEL_ID,
        "ctc_enabled": False,
        "fallback_used": False,
        "warning": warning,
        "note": "Reference-aligned phoneme scoring is active.",
    }
