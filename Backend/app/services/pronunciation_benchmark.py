from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Protocol

from app.config import settings
from app.services.scoring import score_attempt


IssueName = str
ScorePayload = dict[str, Any]
ScoreAttempt = Callable[..., ScorePayload]


OBJECTIVE_CALIBRATION_SOURCES = (
    "native_reference_audio",
    "japanese_mora_phoneme_rules",
    "controlled_error_cases",
    "optional_external_ai_benchmarks",
)

ISSUE_ALIASES: dict[IssueName, set[str]] = {
    "none": {"match"},
    "correct": {"match"},
    "long_vowel": {"long_vowel", "long_vowel_issue"},
    "geminate_pause": {"geminate_pause", "geminate_issue"},
    "small_tsu": {"geminate_pause", "geminate_issue"},
    "mora_nasal": {"mora_nasal", "nasal_issue"},
    "nasal": {"mora_nasal", "nasal_issue"},
    "r_sound": {"r_sound", "r_flap_issue"},
    "r_flap": {"r_sound", "r_flap_issue"},
    "fu_sound": {"fu_sound", "consonant_quality", "substitution"},
    "unrounded_u": {"unrounded_u", "vowel_quality", "vowel_drift"},
    "vowel_quality": {"vowel_quality", "vowel_drift"},
    "extra_vowel": {"extra_vowel", "insertion"},
    "wrong_phrase": {"wrong_phrase"},
}


@dataclass(frozen=True)
class BenchmarkAudio:
    """
    Holds audio either as bytes or as a path. The benchmark harness can run
    inside tests without writing fixture audio, while production calibration can
    point at native/reference clips on disk.
    """

    bytes_data: bytes | None = None
    path: Path | None = None

    @classmethod
    def from_value(cls, value: bytes | str | Path) -> "BenchmarkAudio":
        if isinstance(value, bytes):
            return cls(bytes_data=value)
        return cls(path=Path(value))

    def read(self) -> bytes:
        if self.bytes_data is not None:
            return self.bytes_data
        if self.path is None:
            raise ValueError("Benchmark audio requires bytes_data or path")
        return self.path.read_bytes()

    def label(self) -> str:
        if self.path is not None:
            return str(self.path)
        return "<in-memory-audio>"


@dataclass(frozen=True)
class PronunciationBenchmarkCase:
    case_id: str
    target_text: str
    reference_audio: BenchmarkAudio
    student_audio: BenchmarkAudio
    expected_issue: IssueName = "none"
    expected_min_score: float | None = None
    expected_max_score: float | None = None
    target_romaji: str | None = None
    pronunciation_overrides: dict[str, Any] | None = None
    notes: str | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any], *, base_dir: Path | None = None) -> "PronunciationBenchmarkCase":
        base_dir = base_dir or Path.cwd()
        reference_path = _resolve_audio_path(str(payload["reference_audio_path"]), base_dir)
        student_path = _resolve_audio_path(str(payload["student_audio_path"]), base_dir)
        return cls(
            case_id=str(payload["case_id"]),
            target_text=str(payload["target_text"]),
            target_romaji=_optional_text(payload.get("target_romaji")),
            reference_audio=BenchmarkAudio.from_value(reference_path),
            student_audio=BenchmarkAudio.from_value(student_path),
            expected_issue=str(payload.get("expected_issue", "none")),
            expected_min_score=_optional_float(payload.get("expected_min_score")),
            expected_max_score=_optional_float(payload.get("expected_max_score")),
            pronunciation_overrides=payload.get("pronunciation_overrides") or None,
            notes=_optional_text(payload.get("notes")),
        )


@dataclass(frozen=True)
class ExternalBenchmarkResult:
    provider: str
    status: str
    score: float | None = None
    issues: list[str] = field(default_factory=list)
    warning: str | None = None
    raw: dict[str, Any] | None = None


@dataclass(frozen=True)
class BenchmarkCaseReport:
    case_id: str
    target_text: str
    expected_issue: IssueName
    local_score: float
    detected_issues: list[str]
    passed: bool
    reasons: list[str]
    feedback: list[dict[str, Any]]
    phoneme_count: int
    mora_count: int
    recognizer: dict[str, Any] | None
    external_results: list[ExternalBenchmarkResult]


@dataclass(frozen=True)
class BenchmarkSuiteReport:
    calibration_source: str
    teacher_ground_truth_used: bool
    objective_sources: tuple[str, ...]
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float
    pass_rate_by_issue: dict[str, dict[str, Any]]
    reports: list[BenchmarkCaseReport]

    def to_dict(self) -> dict[str, Any]:
        return {
            "calibration_source": self.calibration_source,
            "teacher_ground_truth_used": self.teacher_ground_truth_used,
            "objective_sources": list(self.objective_sources),
            "total_cases": self.total_cases,
            "passed_cases": self.passed_cases,
            "failed_cases": self.failed_cases,
            "pass_rate": self.pass_rate,
            "pass_rate_by_issue": self.pass_rate_by_issue,
            "reports": [_case_report_to_dict(report) for report in self.reports],
        }


class ExternalBenchmarkProvider(Protocol):
    name: str

    def assess(self, case: PronunciationBenchmarkCase, local_score: ScorePayload) -> ExternalBenchmarkResult:
        ...


class SkippedExternalBenchmarkProvider:
    def __init__(self, name: str, warning: str) -> None:
        self.name = name
        self.warning = warning

    def assess(self, case: PronunciationBenchmarkCase, local_score: ScorePayload) -> ExternalBenchmarkResult:
        return ExternalBenchmarkResult(provider=self.name, status="skipped", warning=self.warning)


def load_benchmark_cases(path: str | Path) -> list[PronunciationBenchmarkCase]:
    """
    Loads objective benchmark cases from JSON. Expected shape:
    [{"case_id": "...", "target_text": "...", "reference_audio_path": "...",
      "student_audio_path": "...", "expected_issue": "long_vowel"}]
    """
    case_path = Path(path)
    raw_cases = json.loads(case_path.read_text(encoding="utf-8"))
    if not isinstance(raw_cases, list):
        raise ValueError("Pronunciation benchmark file must contain a JSON list")
    return [
        PronunciationBenchmarkCase.from_dict(item, base_dir=case_path.parent)
        for item in raw_cases
    ]


def default_external_benchmark_providers() -> list[ExternalBenchmarkProvider]:
    providers: list[ExternalBenchmarkProvider] = []
    if settings.SPEECHSUPER_APP_KEY and settings.SPEECHSUPER_SECRET_KEY:
        providers.append(
            SkippedExternalBenchmarkProvider(
                "speechsuper",
                "SpeechSuper credentials are configured, but the live adapter is intentionally benchmark-only and not implemented in this offline backend.",
            )
        )
    else:
        providers.append(
            SkippedExternalBenchmarkProvider(
                "speechsuper",
                "SpeechSuper benchmark skipped because credentials are not configured.",
            )
        )

    if settings.AZURE_SPEECH_KEY and settings.AZURE_SPEECH_REGION:
        providers.append(
            SkippedExternalBenchmarkProvider(
                "azure_pronunciation_assessment",
                "Azure benchmark adapter is not enabled for Japanese phoneme ground truth; use it only for aggregate comparison.",
            )
        )
    else:
        providers.append(
            SkippedExternalBenchmarkProvider(
                "azure_pronunciation_assessment",
                "Azure benchmark skipped because credentials are not configured.",
            )
        )
    return providers


def run_ai_pronunciation_benchmark(
    cases: list[PronunciationBenchmarkCase],
    *,
    scorer: ScoreAttempt = score_attempt,
    external_providers: list[ExternalBenchmarkProvider] | None = None,
) -> BenchmarkSuiteReport:
    reports = [
        evaluate_benchmark_case(
            case,
            scorer=scorer,
            external_providers=external_providers,
        )
        for case in cases
    ]
    passed_cases = sum(1 for report in reports if report.passed)
    total_cases = len(reports)
    return BenchmarkSuiteReport(
        calibration_source="objective_ai_reference",
        teacher_ground_truth_used=False,
        objective_sources=OBJECTIVE_CALIBRATION_SOURCES,
        total_cases=total_cases,
        passed_cases=passed_cases,
        failed_cases=total_cases - passed_cases,
        pass_rate=round((passed_cases / total_cases) * 100.0, 2) if total_cases else 100.0,
        pass_rate_by_issue=_pass_rate_by_issue(reports),
        reports=reports,
    )


def evaluate_benchmark_case(
    case: PronunciationBenchmarkCase,
    *,
    scorer: ScoreAttempt = score_attempt,
    external_providers: list[ExternalBenchmarkProvider] | None = None,
) -> BenchmarkCaseReport:
    local_score = scorer(
        case.student_audio.read(),
        case.reference_audio.read(),
        target_text=case.target_text,
        target_romaji=case.target_romaji,
        pronunciation_overrides=case.pronunciation_overrides,
    )
    detected_issues = sorted(_detected_issues(local_score))
    expected_issue = case.expected_issue.strip().lower()
    min_score = _minimum_expected_score(case)
    max_score = _maximum_expected_score(case)
    reasons: list[str] = []

    score_value = float(local_score.get("accuracy_score", 0.0))
    expected_aliases = ISSUE_ALIASES.get(expected_issue, {expected_issue})
    is_correct_case = expected_issue in {"none", "correct"}
    is_wrong_phrase_case = expected_issue == "wrong_phrase"
    wrong_phrase_blocked = _looks_like_blocked_wrong_phrase(local_score)
    issue_detected = bool(expected_aliases.intersection(detected_issues))

    if is_correct_case and score_value < min_score:
        reasons.append(f"correct/reference case scored below {min_score:.1f}")
    if is_wrong_phrase_case and not wrong_phrase_blocked and score_value > max_score:
        reasons.append("wrong phrase was not blocked before pronunciation scoring")
    elif not is_correct_case and not is_wrong_phrase_case and score_value > max_score:
        reasons.append(f"known issue case scored above {max_score:.1f}")
    if not is_correct_case and not is_wrong_phrase_case and not issue_detected:
        reasons.append(f"expected issue '{expected_issue}' was not detected")
    if is_correct_case and _has_blocking_issue(detected_issues):
        reasons.append("correct/reference case produced a blocking pronunciation issue")

    external_results = [
        provider.assess(case, local_score)
        for provider in (external_providers if external_providers is not None else default_external_benchmark_providers())
    ]

    phoneme_error_map = local_score.get("phoneme_error_map") or {}
    return BenchmarkCaseReport(
        case_id=case.case_id,
        target_text=case.target_text,
        expected_issue=case.expected_issue,
        local_score=round(score_value, 2),
        detected_issues=detected_issues,
        passed=not reasons,
        reasons=reasons,
        feedback=list(local_score.get("pronunciation_feedback") or []),
        phoneme_count=len(phoneme_error_map.get("phonemes") or []),
        mora_count=len(phoneme_error_map.get("morae") or []),
        recognizer=phoneme_error_map.get("recognizer"),
        external_results=external_results,
    )


def _detected_issues(score_payload: ScorePayload) -> set[str]:
    issues: set[str] = set()
    for item in score_payload.get("pronunciation_feedback") or []:
        issue = str(item.get("issue_type", "")).strip().lower()
        if issue:
            issues.add(issue)

    phoneme_error_map = score_payload.get("phoneme_error_map") or {}
    for item in phoneme_error_map.get("phonemes") or []:
        issue = str(item.get("issue_type", "")).strip().lower()
        operation = str(item.get("operation", "")).strip().lower()
        if issue and issue != "match":
            issues.add(issue)
        if operation and operation != "match":
            issues.add(operation)

    for name in ("mora_timing", "consonants", "vowels", "phoneme_match", "fluency"):
        category = phoneme_error_map.get(name) or {}
        if category.get("error"):
            issues.add(name)
    return issues or {"match"}


def _pass_rate_by_issue(reports: list[BenchmarkCaseReport]) -> dict[str, dict[str, Any]]:
    totals: dict[str, dict[str, Any]] = {}
    for report in reports:
        issue = report.expected_issue
        bucket = totals.setdefault(issue, {"total": 0, "passed": 0, "pass_rate": 0.0})
        bucket["total"] += 1
        if report.passed:
            bucket["passed"] += 1

    for bucket in totals.values():
        total = int(bucket["total"])
        passed = int(bucket["passed"])
        bucket["pass_rate"] = round((passed / total) * 100.0, 2) if total else 100.0

    return totals


def _minimum_expected_score(case: PronunciationBenchmarkCase) -> float:
    if case.expected_min_score is not None:
        return case.expected_min_score
    return float(settings.PRONUNCIATION_BENCHMARK_MIN_CORRECT_SCORE)


def _maximum_expected_score(case: PronunciationBenchmarkCase) -> float:
    if case.expected_max_score is not None:
        return case.expected_max_score
    return float(settings.PRONUNCIATION_BENCHMARK_MAX_ISSUE_SCORE)


def _has_blocking_issue(detected_issues: list[str]) -> bool:
    return any(issue not in {"match"} for issue in detected_issues)


def _looks_like_blocked_wrong_phrase(score_payload: ScorePayload) -> bool:
    feedback_text = str(score_payload.get("feedback_text", "")).lower()
    return (
        float(score_payload.get("accuracy_score", 0.0)) <= 0.0
        and score_payload.get("phoneme_error_map") is None
        and (
            "wrong phrase" in feedback_text
            or "verification" in feedback_text
            or "try the target phrase" in feedback_text
        )
    )


def _case_report_to_dict(report: BenchmarkCaseReport) -> dict[str, Any]:
    return {
        "case_id": report.case_id,
        "target_text": report.target_text,
        "expected_issue": report.expected_issue,
        "local_score": report.local_score,
        "detected_issues": report.detected_issues,
        "passed": report.passed,
        "reasons": report.reasons,
        "feedback": report.feedback,
        "phoneme_count": report.phoneme_count,
        "mora_count": report.mora_count,
        "recognizer": report.recognizer,
        "external_results": [
            {
                "provider": item.provider,
                "status": item.status,
                "score": item.score,
                "issues": item.issues,
                "warning": item.warning,
                "raw": item.raw,
            }
            for item in report.external_results
        ],
    }


def _resolve_audio_path(value: str, base_dir: Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else base_dir / path


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)
