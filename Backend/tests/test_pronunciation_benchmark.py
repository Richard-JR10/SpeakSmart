import json

from app.services.pronunciation_benchmark import (
    BenchmarkAudio,
    PronunciationBenchmarkCase,
    load_benchmark_cases,
    run_ai_pronunciation_benchmark,
)


def test_benchmark_uses_objective_ai_reference_not_teacher_labels():
    cases = [
        PronunciationBenchmarkCase(
            case_id="native-reference",
            target_text="\u3042\u308a\u304c\u3068\u3046",
            reference_audio=BenchmarkAudio.from_value(b"reference"),
            student_audio=BenchmarkAudio.from_value(b"student"),
            expected_issue="none",
        )
    ]

    report = run_ai_pronunciation_benchmark(cases, scorer=_scorer(score=94.0))

    assert report.calibration_source == "objective_ai_reference"
    assert report.teacher_ground_truth_used is False
    assert "native_reference_audio" in report.objective_sources
    assert report.pass_rate == 100.0
    assert report.pass_rate_by_issue["none"]["pass_rate"] == 100.0


def test_benchmark_flags_known_issue_when_ai_does_not_detect_it():
    cases = [
        PronunciationBenchmarkCase(
            case_id="missing-small-tsu",
            target_text="\u304d\u3063\u3066",
            reference_audio=BenchmarkAudio.from_value(b"reference"),
            student_audio=BenchmarkAudio.from_value(b"student"),
            expected_issue="small_tsu",
        )
    ]

    report = run_ai_pronunciation_benchmark(cases, scorer=_scorer(score=96.0))
    case_report = report.reports[0]

    assert case_report.passed is False
    assert any("small_tsu" in reason for reason in case_report.reasons)
    assert any("above" in reason for reason in case_report.reasons)


def test_benchmark_passes_when_targeted_issue_is_detected():
    cases = [
        PronunciationBenchmarkCase(
            case_id="clipped-long-vowel",
            target_text="\u3042\u308a\u304c\u3068\u3046",
            reference_audio=BenchmarkAudio.from_value(b"reference"),
            student_audio=BenchmarkAudio.from_value(b"student"),
            expected_issue="long_vowel",
        )
    ]

    report = run_ai_pronunciation_benchmark(
        cases,
        scorer=_scorer(score=74.0, issue_type="long_vowel_issue", operation="duration_error"),
    )

    assert report.passed_cases == 1
    assert report.reports[0].detected_issues == ["duration_error", "long_vowel_issue"]


def test_benchmark_accepts_wrong_phrase_blocked_before_scoring():
    cases = [
        PronunciationBenchmarkCase(
            case_id="wrong-phrase",
            target_text="\u3042\u308a\u304c\u3068\u3046",
            reference_audio=BenchmarkAudio.from_value(b"reference"),
            student_audio=BenchmarkAudio.from_value(b"student"),
            expected_issue="wrong_phrase",
        )
    ]

    report = run_ai_pronunciation_benchmark(cases, scorer=_blocked_wrong_phrase_scorer)

    assert report.passed_cases == 1
    assert report.reports[0].passed is True


def test_load_benchmark_cases_resolves_paths_relative_to_json(tmp_path):
    reference = tmp_path / "reference.wav"
    student = tmp_path / "student.wav"
    reference.write_bytes(b"reference")
    student.write_bytes(b"student")
    case_path = tmp_path / "cases.json"
    case_path.write_text(
        json.dumps(
            [
                {
                    "case_id": "r-flap",
                    "target_text": "\u308a",
                    "reference_audio_path": "reference.wav",
                    "student_audio_path": "student.wav",
                    "expected_issue": "r_sound",
                }
            ]
        ),
        encoding="utf-8",
    )

    cases = load_benchmark_cases(case_path)

    assert cases[0].reference_audio.read() == b"reference"
    assert cases[0].student_audio.read() == b"student"
    assert cases[0].expected_issue == "r_sound"


def _scorer(*, score: float, issue_type: str = "match", operation: str = "match"):
    def score_attempt_stub(student_audio: bytes, reference_audio: bytes, **kwargs):
        assert student_audio == b"student"
        assert reference_audio == b"reference"
        return {
            "accuracy_score": score,
            "mora_timing_score": score,
            "consonant_score": score,
            "vowel_score": score,
            "phoneme_error_map": {
                "phonemes": [
                    {
                        "expected_phoneme": "a",
                        "heard_phoneme": "a",
                        "issue_type": issue_type,
                        "operation": operation,
                    }
                ],
                "morae": [{"score": score}],
                "recognizer": {"provider": "mock-ai"},
            },
            "feedback_text": "",
            "target_pronunciation": {},
            "pronunciation_feedback": []
            if issue_type == "match"
            else [{"issue_type": issue_type, "score": score}],
        }

    return score_attempt_stub


def _blocked_wrong_phrase_scorer(student_audio: bytes, reference_audio: bytes, **kwargs):
    assert student_audio == b"student"
    assert reference_audio == b"reference"
    return {
        "accuracy_score": 0.0,
        "mora_timing_score": 0.0,
        "consonant_score": 0.0,
        "vowel_score": 0.0,
        "phoneme_error_map": None,
        "feedback_text": "Phrase verification was uncertain. Please try the target phrase again.",
        "target_pronunciation": {},
        "pronunciation_feedback": [],
    }
