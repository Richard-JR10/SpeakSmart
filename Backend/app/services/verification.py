import logging
import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher

from app.config import settings
from app.services.asr import ASRTranscript, transcribe_audio_bytes
from app.services.speech import extract_features

VERIFICATION_ACCEPTED = "accepted"
VERIFICATION_WRONG_PHRASE = "wrong_phrase_detected"
VERIFICATION_NO_CLEAR_SPEECH = "no_clear_speech"
VERIFICATION_RETRY = "retry_needed"

_NORMALIZE_PATTERN = re.compile(
    r"[\s\-\_\.\,\!\?\:\;\(\)\[\]\{\}\u3001\u3002\u30fb\u30fc\"'`~]+"
)
_JAPANESE_CHAR_PATTERN = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]")
_KANA_DIGRAPHS = {
    "きゃ": "kya",
    "きゅ": "kyu",
    "きょ": "kyo",
    "ぎゃ": "gya",
    "ぎゅ": "gyu",
    "ぎょ": "gyo",
    "しゃ": "sha",
    "しゅ": "shu",
    "しょ": "sho",
    "じゃ": "ja",
    "じゅ": "ju",
    "じょ": "jo",
    "ちゃ": "cha",
    "ちゅ": "chu",
    "ちょ": "cho",
    "にゃ": "nya",
    "にゅ": "nyu",
    "にょ": "nyo",
    "ひゃ": "hya",
    "ひゅ": "hyu",
    "ひょ": "hyo",
    "びゃ": "bya",
    "びゅ": "byu",
    "びょ": "byo",
    "ぴゃ": "pya",
    "ぴゅ": "pyu",
    "ぴょ": "pyo",
    "みゃ": "mya",
    "みゅ": "myu",
    "みょ": "myo",
    "りゃ": "rya",
    "りゅ": "ryu",
    "りょ": "ryo",
}
_KANA_ROMAJI = {
    "あ": "a",
    "い": "i",
    "う": "u",
    "え": "e",
    "お": "o",
    "か": "ka",
    "き": "ki",
    "く": "ku",
    "け": "ke",
    "こ": "ko",
    "が": "ga",
    "ぎ": "gi",
    "ぐ": "gu",
    "げ": "ge",
    "ご": "go",
    "さ": "sa",
    "し": "shi",
    "す": "su",
    "せ": "se",
    "そ": "so",
    "ざ": "za",
    "じ": "ji",
    "ず": "zu",
    "ぜ": "ze",
    "ぞ": "zo",
    "た": "ta",
    "ち": "chi",
    "つ": "tsu",
    "て": "te",
    "と": "to",
    "だ": "da",
    "ぢ": "ji",
    "づ": "zu",
    "で": "de",
    "ど": "do",
    "な": "na",
    "に": "ni",
    "ぬ": "nu",
    "ね": "ne",
    "の": "no",
    "は": "ha",
    "ひ": "hi",
    "ふ": "fu",
    "へ": "he",
    "ほ": "ho",
    "ば": "ba",
    "び": "bi",
    "ぶ": "bu",
    "べ": "be",
    "ぼ": "bo",
    "ぱ": "pa",
    "ぴ": "pi",
    "ぷ": "pu",
    "ぺ": "pe",
    "ぽ": "po",
    "ま": "ma",
    "み": "mi",
    "む": "mu",
    "め": "me",
    "も": "mo",
    "や": "ya",
    "ゆ": "yu",
    "よ": "yo",
    "ら": "ra",
    "り": "ri",
    "る": "ru",
    "れ": "re",
    "ろ": "ro",
    "わ": "wa",
    "を": "wo",
    "ん": "n",
    "ぁ": "a",
    "ぃ": "i",
    "ぅ": "u",
    "ぇ": "e",
    "ぉ": "o",
    "ゎ": "wa",
}
logger = logging.getLogger("speaksmart.verification")
logger.setLevel(logging.INFO)


@dataclass(frozen=True)
class VerificationCandidate:
    phrase_id: str
    japanese_text: str
    normalized_text: str


@dataclass(frozen=True)
class CandidateScore:
    phrase_id: str
    score: float


@dataclass(frozen=True)
class VerificationResult:
    status: str
    recognized_phrase_id: str | None
    recognized_text: str | None
    recognized_text_romaji: str | None
    verification_confidence: float | None
    verification_margin: float | None


def normalize_phrase_text(text: str | None) -> str:
    if not text:
        return ""

    normalized = unicodedata.normalize("NFKC", text).lower()
    normalized = _katakana_to_hiragana(normalized)
    normalized = _NORMALIZE_PATTERN.sub("", normalized)
    return normalized.strip()


def format_recognized_text_for_feedback(text: str | None) -> str | None:
    if not text:
        return None

    collapsed = " ".join(text.strip().split())
    romaji = kana_to_romaji(collapsed)
    romaji = _apply_particle_pronunciation(collapsed, romaji)
    if romaji and romaji != collapsed:
        return " ".join(part.capitalize() for part in romaji.split())
    return collapsed


def kana_to_romaji(text: str | None) -> str:
    if not text:
        return ""

    normalized = _katakana_to_hiragana(unicodedata.normalize("NFKC", text).lower())
    result: list[str] = []
    geminate_next = False
    index = 0

    while index < len(normalized):
        pair = normalized[index:index + 2]
        char = normalized[index]

        if pair in _KANA_DIGRAPHS:
            romaji = _KANA_DIGRAPHS[pair]
            index += 2
        elif char == "っ":
            geminate_next = True
            index += 1
            continue
        elif char == "ー":
            if result:
                last_vowel = _last_vowel(result[-1])
                if last_vowel:
                    result.append(last_vowel)
            index += 1
            continue
        else:
            romaji = _KANA_ROMAJI.get(char, char)
            index += 1

        if geminate_next and romaji and romaji[0].isalpha():
            result.append(romaji[0])
        geminate_next = False
        result.append(romaji)

    return "".join(result)


def select_verification_candidates(
    target_phrase_id: str,
    target_text: str,
    candidates: list[tuple[str, str]],
    max_candidates: int | None = None,
) -> list[VerificationCandidate]:
    max_candidates = max_candidates or settings.VERIFICATION_MAX_CANDIDATES
    normalized_target = normalize_phrase_text(target_text)

    unique_candidates: dict[str, VerificationCandidate] = {}
    for phrase_id, japanese_text in candidates:
        unique_candidates[phrase_id] = VerificationCandidate(
            phrase_id=phrase_id,
            japanese_text=japanese_text,
            normalized_text=normalize_phrase_text(japanese_text),
        )

    if target_phrase_id not in unique_candidates:
        unique_candidates[target_phrase_id] = VerificationCandidate(
            phrase_id=target_phrase_id,
            japanese_text=target_text,
            normalized_text=normalized_target,
        )

    def priority(item: VerificationCandidate) -> tuple[int, float, str]:
        if item.phrase_id == target_phrase_id:
            return (0, -1.0, item.phrase_id)

        similarity = SequenceMatcher(
            None,
            normalized_target,
            item.normalized_text,
        ).ratio()
        return (1, -similarity, item.phrase_id)

    ordered = sorted(unique_candidates.values(), key=priority)
    return ordered[:max_candidates]


def compute_candidate_scores(
    recognized_text: str,
    candidates: list[VerificationCandidate],
) -> list[CandidateScore]:
    normalized_recognized = normalize_phrase_text(recognized_text)
    if not normalized_recognized:
        return [CandidateScore(candidate.phrase_id, 0.0) for candidate in candidates]

    scores: list[CandidateScore] = []
    for candidate in candidates:
        ratio = SequenceMatcher(
            None,
            normalized_recognized,
            candidate.normalized_text,
        ).ratio()
        prefix_bonus = 0.05 if (
            normalized_recognized.startswith(candidate.normalized_text)
            or candidate.normalized_text.startswith(normalized_recognized)
        ) else 0.0
        if normalized_recognized == candidate.normalized_text:
            ratio = 1.0
        scores.append(
            CandidateScore(
                phrase_id=candidate.phrase_id,
                score=min(1.0, ratio + prefix_bonus),
            )
        )

    return sorted(scores, key=lambda item: item.score, reverse=True)


def sanitize_transcript(
    transcript: str,
    candidates: list[VerificationCandidate],
) -> str:
    cleaned = " ".join(transcript.strip().split())
    if not cleaned:
        return ""

    normalized_cleaned = normalize_phrase_text(cleaned)
    if not normalized_cleaned:
        return ""

    collapsed_candidate = _collapse_repeated_candidate(
        cleaned,
        normalized_cleaned,
        candidates,
    )
    if collapsed_candidate is not None:
        return collapsed_candidate

    return cleaned


def classify_verification_result(
    target_phrase_id: str,
    recognized_text: str | None,
    candidates: list[VerificationCandidate],
    voiced_ratio: float,
    *,
    acceptance_confidence: float | None = None,
    wrong_phrase_confidence: float | None = None,
    min_margin: float | None = None,
) -> VerificationResult:
    acceptance_confidence = (
        settings.VERIFICATION_ACCEPTANCE_CONFIDENCE
        if acceptance_confidence is None
        else acceptance_confidence
    )
    wrong_phrase_confidence = (
        settings.VERIFICATION_WRONG_PHRASE_CONFIDENCE
        if wrong_phrase_confidence is None
        else wrong_phrase_confidence
    )
    min_margin = settings.VERIFICATION_MIN_MARGIN if min_margin is None else min_margin

    normalized_recognized = normalize_phrase_text(recognized_text)
    recognized_text_romaji = format_recognized_text_for_feedback(recognized_text)
    if not normalized_recognized:
        status = (
            VERIFICATION_NO_CLEAR_SPEECH
            if voiced_ratio < settings.VERIFICATION_MIN_VOICED_RATIO
            else VERIFICATION_RETRY
        )
        return VerificationResult(
            status=status,
            recognized_phrase_id=None,
            recognized_text=recognized_text,
            recognized_text_romaji=recognized_text_romaji,
            verification_confidence=0.0,
            verification_margin=0.0,
        )

    scores = compute_candidate_scores(normalized_recognized, candidates)
    best = scores[0]
    second_best = scores[1] if len(scores) > 1 else CandidateScore(phrase_id="", score=0.0)
    margin = round(best.score - second_best.score, 4)
    confidence = round(best.score, 4)

    if (
        best.phrase_id == target_phrase_id
        and best.score >= acceptance_confidence
        and margin >= min_margin
    ):
        status = VERIFICATION_ACCEPTED
    elif (
        best.phrase_id != target_phrase_id
        and best.score >= wrong_phrase_confidence
        and margin >= min_margin
    ):
        status = VERIFICATION_WRONG_PHRASE
    else:
        status = VERIFICATION_RETRY

    logger.info(
        "verification classified target=%s recognized_phrase=%s status=%s confidence=%.4f margin=%.4f transcript=%s top_scores=%s",
        target_phrase_id,
        best.phrase_id if best.score > 0 else None,
        status,
        confidence,
        margin,
        _truncate_for_log(recognized_text),
        [
            {
                "phrase_id": item.phrase_id,
                "score": round(item.score, 4),
            }
            for item in scores[:3]
        ],
    )

    return VerificationResult(
        status=status,
        recognized_phrase_id=best.phrase_id if best.score > 0 and status != VERIFICATION_RETRY else None,
        recognized_text=recognized_text,
        recognized_text_romaji=recognized_text_romaji,
        verification_confidence=confidence,
        verification_margin=margin,
    )


def verify_phrase_audio(
    audio_bytes: bytes,
    target_phrase_id: str,
    target_text: str,
    candidate_pairs: list[tuple[str, str]],
) -> VerificationResult:
    feature_data = extract_features(audio_bytes)
    voiced_ratio = float(feature_data.get("voiced_ratio", 0.0))
    logger.info(
        "verification started target=%s voiced_ratio=%.4f duration=%.2fs rms=%.6f candidate_count=%d",
        target_phrase_id,
        voiced_ratio,
        float(feature_data.get("duration", 0.0)),
        float(feature_data.get("rms", 0.0)),
        len(candidate_pairs),
    )
    if voiced_ratio < settings.VERIFICATION_MIN_VOICED_RATIO:
        logger.info(
            "verification blocked target=%s reason=no_clear_speech voiced_ratio=%.4f threshold=%.4f",
            target_phrase_id,
            voiced_ratio,
            settings.VERIFICATION_MIN_VOICED_RATIO,
        )
        return VerificationResult(
            status=VERIFICATION_NO_CLEAR_SPEECH,
            recognized_phrase_id=None,
            recognized_text=None,
            recognized_text_romaji=None,
            verification_confidence=0.0,
            verification_margin=0.0,
        )

    candidates = select_verification_candidates(
        target_phrase_id=target_phrase_id,
        target_text=target_text,
        candidates=candidate_pairs,
    )
    transcript = transcribe_audio_bytes(audio_bytes)
    recognized_text = sanitize_transcript(transcript.text, candidates)
    logger.info(
        "verification transcript target=%s transcript=%s transcript_language=%s avg_logprob=%s no_speech_prob=%s compression_ratio=%s",
        target_phrase_id,
        _truncate_for_log(recognized_text),
        transcript.language,
        transcript.avg_logprob,
        transcript.no_speech_prob,
        transcript.compression_ratio,
    )

    if transcript.no_speech_prob is not None and transcript.no_speech_prob >= 0.6 and not recognized_text:
        return VerificationResult(
            status=VERIFICATION_NO_CLEAR_SPEECH,
            recognized_phrase_id=None,
            recognized_text=recognized_text,
            recognized_text_romaji=format_recognized_text_for_feedback(recognized_text),
            verification_confidence=0.0,
            verification_margin=0.0,
        )

    return classify_verification_result(
        target_phrase_id=target_phrase_id,
        recognized_text=recognized_text,
        candidates=candidates,
        voiced_ratio=voiced_ratio,
    )


def _collapse_repeated_candidate(
    transcript: str,
    normalized_transcript: str,
    candidates: list[VerificationCandidate],
) -> str | None:
    for candidate in candidates:
        unit = candidate.normalized_text
        if not unit:
            continue
        if len(normalized_transcript) < len(unit) * 2:
            continue
        if len(normalized_transcript) % len(unit) != 0:
            continue

        repetition_count = len(normalized_transcript) // len(unit)
        if repetition_count < 2:
            continue

        if normalized_transcript == unit * repetition_count:
            logger.info(
                "verification collapsed repeated transcript raw=%s candidate=%s repetitions=%d",
                _truncate_for_log(transcript),
                candidate.phrase_id,
                repetition_count,
            )
            return candidate.japanese_text

    return None


def _katakana_to_hiragana(text: str) -> str:
    converted: list[str] = []
    for char in text:
        codepoint = ord(char)
        if 0x30A1 <= codepoint <= 0x30F6:
            converted.append(chr(codepoint - 0x60))
        else:
            converted.append(char)
    return "".join(converted)


def _last_vowel(value: str) -> str:
    for char in reversed(value):
        if char in "aeiou":
            return char
    return ""


def _apply_particle_pronunciation(source_text: str, romaji: str) -> str:
    normalized = _katakana_to_hiragana(unicodedata.normalize("NFKC", source_text).lower())
    if normalized.endswith("は") and romaji.endswith("ha"):
        return f"{romaji[:-2]}wa"
    if normalized.endswith("へ") and romaji.endswith("he"):
        return f"{romaji[:-2]}e"
    if normalized.endswith("を") and romaji.endswith("wo"):
        return f"{romaji[:-2]}o"
    return romaji


def _truncate_for_log(value: str | None, limit: int = 160) -> str | None:
    if value is None:
        return None
    if len(value) <= limit:
        return value
    return f"{value[:limit]}..."
