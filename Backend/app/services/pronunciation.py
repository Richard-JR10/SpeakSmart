from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from pykakasi import kakasi


_SMALL_KANA = set("ゃゅょぁぃぅぇぉゎャュョァィゥェォヮ")
_DIGRAPH_MARKERS = set("ゃゅょャュョ")
_VOICELESS_ONSETS = ("k", "s", "t", "h", "p", "ky", "sh", "ch", "ts")
_PUNCTUATION_PATTERN = re.compile(r"[\s、。・,.!?\"'()\-]+")


@dataclass(frozen=True)
class PronunciationChunk:
    index: int
    display_text: str
    kana: str
    romaji: str
    source_text: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "display_text": self.display_text,
            "kana": self.kana,
            "romaji": self.romaji,
        }


@dataclass(frozen=True)
class PronunciationRule:
    chunk_index: int
    issue_type: str
    expected_note: str
    fix_tip: str
    threshold: float = 82.0


def build_target_pronunciation(
    text: str,
    *,
    romaji_hint: str | None = None,
    reading_override: str | None = None,
    chunk_override: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    chunks = _build_chunks(
        text=text,
        reading_override=reading_override,
        chunk_override=chunk_override,
    )
    kana = "".join(chunk.kana for chunk in chunks)
    romaji = _normalize_romaji_guide(romaji_hint) or " ".join(
        chunk.romaji for chunk in chunks
    )

    payload = {
        "kana": kana,
        "romaji": romaji,
        "chunks": [chunk.to_payload() for chunk in chunks],
    }
    from app.services.phoneme_assessment import enrich_target_pronunciation

    return enrich_target_pronunciation(payload)


def build_pronunciation_rules(
    text: str,
    target_pronunciation: dict[str, Any],
    *,
    rule_override: dict[str, Any] | None = None,
) -> list[PronunciationRule]:
    chunks = _payload_to_chunks(target_pronunciation.get("chunks", []))
    overrides = rule_override or {}
    rules: list[PronunciationRule] = []

    for index, chunk in enumerate(chunks):
        rule = _build_rule_for_chunk(text, chunks, index, chunk)
        override = overrides.get(str(index)) if isinstance(overrides, dict) else None
        if override:
            rule = PronunciationRule(
                chunk_index=index,
                issue_type=str(override.get("issue_type", rule.issue_type)),
                expected_note=str(override.get("expected_note", rule.expected_note)),
                fix_tip=str(override.get("fix_tip", rule.fix_tip)),
                threshold=float(override.get("threshold", rule.threshold)),
            )
        rules.append(rule)

    return rules


def summarize_pronunciation_feedback(
    feedback_items: list[dict[str, Any]],
) -> str:
    if not feedback_items:
        return (
            "Strong pronunciation overall. Keep the same rhythm and light "
            "Japanese vowel quality on the next try."
        )

    top_items = feedback_items[:2]
    if len(top_items) == 1:
        return top_items[0]["fix_tip"]

    return f"{top_items[0]['fix_tip']} Then {top_items[1]['fix_tip'].lower()}"


def get_pronunciation_overrides(phrase: Any) -> dict[str, Any]:
    return {
        "reading_override": getattr(phrase, "pronunciation_reading_override", None),
        "chunk_override": getattr(phrase, "pronunciation_chunk_override", None),
        "rule_override": getattr(phrase, "pronunciation_rule_override", None),
    }


def build_reference_target_from_phrase(phrase: Any) -> dict[str, Any]:
    overrides = get_pronunciation_overrides(phrase)
    return build_target_pronunciation(
        phrase.japanese_text,
        romaji_hint=getattr(phrase, "romaji", None),
        reading_override=overrides.get("reading_override"),
        chunk_override=overrides.get("chunk_override"),
    )


@lru_cache(maxsize=1)
def _get_kakasi():
    return kakasi()


def _build_chunks(
    *,
    text: str,
    reading_override: str | None,
    chunk_override: list[dict[str, Any]] | None,
) -> list[PronunciationChunk]:
    if chunk_override:
        override_chunks = _normalize_chunk_override(chunk_override)
        if override_chunks:
            return override_chunks

    if reading_override:
        reading = _normalize_kana(reading_override)
        return _chunks_from_reading(reading)

    token_entries = _readings_from_text(text)
    if not token_entries:
        return _chunks_from_reading(_normalize_kana(text))

    chunks: list[PronunciationChunk] = []
    for entry in token_entries:
        reading = _normalize_kana(entry["reading"])
        if not reading:
            continue

        token_chunks = _split_into_chunks(reading)
        for chunk_text in token_chunks:
            chunk_index = len(chunks)
            romaji = _chunk_to_romaji(
                chunk_text,
                source_text=entry["orig"],
                is_last_chunk=False,
            )
            chunks.append(
                PronunciationChunk(
                    index=chunk_index,
                    display_text=chunk_text,
                    kana=chunk_text,
                    romaji=romaji,
                    source_text=entry["orig"],
                )
            )

    if chunks:
        last_chunk = chunks[-1]
        chunks[-1] = PronunciationChunk(
            index=last_chunk.index,
            display_text=last_chunk.display_text,
            kana=last_chunk.kana,
            romaji=_chunk_to_romaji(
                last_chunk.kana,
                source_text=last_chunk.source_text,
                is_last_chunk=True,
            ),
            source_text=last_chunk.source_text,
        )

    return chunks


def _normalize_chunk_override(
    chunk_override: list[dict[str, Any]],
) -> list[PronunciationChunk]:
    chunks: list[PronunciationChunk] = []
    for index, item in enumerate(chunk_override):
        kana = _normalize_kana(str(item.get("kana", item.get("display_text", ""))))
        if not kana:
            continue
        romaji = _normalize_romaji_guide(item.get("romaji")) or _chunk_to_romaji(
            kana,
            source_text=item.get("display_text"),
            is_last_chunk=index == len(chunk_override) - 1,
        )
        chunks.append(
            PronunciationChunk(
                index=index,
                display_text=str(item.get("display_text", kana)),
                kana=kana,
                romaji=romaji,
                source_text=str(item.get("display_text", kana)),
            )
        )
    return chunks


def _readings_from_text(text: str) -> list[dict[str, str]]:
    converted = _get_kakasi().convert(text)
    entries: list[dict[str, str]] = []

    for part in converted:
        original = str(part.get("orig", "")).strip()
        reading = str(part.get("hira", original)).strip()
        if not original:
            continue
        entries.append({"orig": original, "reading": reading})

    return entries


def _chunks_from_reading(reading: str) -> list[PronunciationChunk]:
    normalized = _normalize_kana(reading)
    token_chunks = _split_into_chunks(normalized)
    chunks: list[PronunciationChunk] = []
    for index, chunk_text in enumerate(token_chunks):
        chunks.append(
            PronunciationChunk(
                index=index,
                display_text=chunk_text,
                kana=chunk_text,
                romaji=_chunk_to_romaji(
                    chunk_text,
                    source_text=chunk_text,
                    is_last_chunk=index == len(token_chunks) - 1,
                ),
                source_text=chunk_text,
            )
        )
    return chunks


def _split_into_chunks(reading: str) -> list[str]:
    chunks: list[str] = []
    for char in reading:
        if not chunks:
            chunks.append(char)
            continue

        if char in _SMALL_KANA or char == "ー":
            chunks[-1] = f"{chunks[-1]}{char}"
            continue

        chunks.append(char)

    return [chunk for chunk in chunks if chunk and not _PUNCTUATION_PATTERN.fullmatch(chunk)]


def _payload_to_chunks(payload: list[dict[str, Any]]) -> list[PronunciationChunk]:
    chunks: list[PronunciationChunk] = []
    for index, item in enumerate(payload):
        chunks.append(
            PronunciationChunk(
                index=index,
                display_text=str(item.get("display_text", item.get("kana", ""))),
                kana=_normalize_kana(str(item.get("kana", item.get("display_text", "")))),
                romaji=_normalize_romaji_guide(item.get("romaji")) or "",
                source_text=str(item.get("display_text", item.get("kana", ""))),
            )
        )
    return chunks


def _build_rule_for_chunk(
    text: str,
    chunks: list[PronunciationChunk],
    index: int,
    chunk: PronunciationChunk,
) -> PronunciationRule:
    if _is_particle_chunk(index, chunk, chunks):
        spoken = {"は": "wa", "へ": "e", "を": "o"}.get(chunk.kana, chunk.romaji)
        return PronunciationRule(
            chunk_index=index,
            issue_type="particle_pronunciation",
            expected_note=f"This chunk is written as {chunk.kana} but spoken as {spoken}.",
            fix_tip=f"Say {spoken} here instead of the literal written sound.",
            threshold=88.0,
        )

    if chunk.kana == "っ":
        return PronunciationRule(
            chunk_index=index,
            issue_type="geminate_pause",
            expected_note="This small tsu should sound like a brief held pause before the next consonant.",
            fix_tip="Hold a tiny pause before the next consonant instead of running through it.",
            threshold=84.0,
        )

    if chunk.kana == "ん":
        return PronunciationRule(
            chunk_index=index,
            issue_type="mora_nasal",
            expected_note="This mora is the Japanese nasal sound and should stay distinct.",
            fix_tip="Keep the nasal sound clear without adding an extra vowel after it.",
            threshold=82.0,
        )

    if _has_contracted_sound(chunk.kana):
        return PronunciationRule(
            chunk_index=index,
            issue_type="contracted_sound",
            expected_note="This is a blended Japanese sound and should stay compact in one beat.",
            fix_tip="Blend this sound smoothly into one compact chunk.",
            threshold=82.0,
        )

    if _is_long_vowel_chunk(chunks, index):
        return PronunciationRule(
            chunk_index=index,
            issue_type="long_vowel",
            expected_note="This part forms a long vowel and should be held for a full extra beat.",
            fix_tip="Hold this vowel for an extra mora instead of clipping it short.",
            threshold=84.0,
        )

    if _is_devoicing_candidate(chunks, index):
        return PronunciationRule(
            chunk_index=index,
            issue_type="devoicing",
            expected_note="This ending is often very soft in natural Japanese speech.",
            fix_tip="Lighten this ending and avoid pronouncing the final vowel too strongly.",
            threshold=88.0,
        )

    if chunk.romaji.startswith("r"):
        return PronunciationRule(
            chunk_index=index,
            issue_type="r_sound",
            expected_note="Japanese r-sounds are light flaps, not heavy English r sounds.",
            fix_tip="Use a light Japanese r-flap instead of a strong English-style r.",
            threshold=80.0,
        )

    if _chunk_has_pure_vowel(chunk.romaji):
        return PronunciationRule(
            chunk_index=index,
            issue_type="vowel_quality",
            expected_note="Japanese vowels should stay pure and steady without sliding.",
            fix_tip="Keep the vowel pure and steady instead of gliding into another sound.",
            threshold=80.0,
        )

    return PronunciationRule(
        chunk_index=index,
        issue_type="consonant_quality",
        expected_note="This sound should stay crisp and clearly separated.",
        fix_tip="Make this consonant cleaner and more controlled on the next try.",
        threshold=80.0,
    )


def _is_particle_chunk(
    index: int,
    chunk: PronunciationChunk,
    chunks: list[PronunciationChunk],
) -> bool:
    if chunk.kana == "を":
        return True

    source_text = (chunk.source_text or "").strip()
    if source_text in {"は", "へ", "を"}:
        return True

    if index == len(chunks) - 1 and chunk.kana in {"は", "へ"}:
        return True

    return False


def _is_devoicing_candidate(
    chunks: list[PronunciationChunk],
    index: int,
) -> bool:
    chunk = chunks[index]
    if chunk.romaji not in {"su", "shi", "tsu", "chi", "ku", "ki", "pu", "pi", "fu", "hi"}:
        return False

    if index == len(chunks) - 1:
        return True

    previous = chunks[index - 1].romaji if index > 0 else ""
    following = chunks[index + 1].romaji if index + 1 < len(chunks) else ""

    return _starts_with_voiceless(previous) and _starts_with_voiceless(following)


def _is_long_vowel_chunk(
    chunks: list[PronunciationChunk],
    index: int,
) -> bool:
    if index == 0:
        return False

    current_vowel = _final_vowel(chunks[index].romaji)
    previous_vowel = _final_vowel(chunks[index - 1].romaji)
    return bool(current_vowel and current_vowel == previous_vowel)


def _has_contracted_sound(kana: str) -> bool:
    return any(marker in kana for marker in _DIGRAPH_MARKERS)


def _chunk_has_pure_vowel(romaji: str) -> bool:
    return any(vowel in romaji for vowel in ("a", "i", "u", "e", "o"))


def _starts_with_voiceless(romaji: str) -> bool:
    return any(romaji.startswith(prefix) for prefix in _VOICELESS_ONSETS)


def _final_vowel(romaji: str) -> str:
    for char in reversed(romaji):
        if char in "aeiou":
            return char
    return ""


def _chunk_to_romaji(
    chunk: str,
    *,
    source_text: str | None,
    is_last_chunk: bool,
) -> str:
    converted = _get_kakasi().convert(chunk)
    base = "".join(str(part.get("hepburn", part.get("orig", ""))) for part in converted)
    normalized = _normalize_romaji_guide(base) or _normalize_romaji_guide(chunk) or chunk

    source = (source_text or "").strip()
    if source == "は":
        return "wa"
    if source == "へ":
        return "e"
    if source == "を":
        return "o"

    if is_last_chunk and normalized == "ha" and chunk == "は":
        return "wa"
    if is_last_chunk and normalized == "he" and chunk == "へ":
        return "e"

    if normalized == "xtsu":
        return "pause"

    return normalized


def _normalize_kana(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).strip()
    converted: list[str] = []
    for char in normalized:
        codepoint = ord(char)
        if 0x30A1 <= codepoint <= 0x30F6:
            converted.append(chr(codepoint - 0x60))
        else:
            converted.append(char)
    return "".join(converted)


def _normalize_romaji_guide(value: Any) -> str | None:
    if value is None:
        return None

    collapsed = " ".join(str(value).strip().split())
    if not collapsed:
        return None
    return collapsed.lower()
