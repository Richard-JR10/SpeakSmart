from datetime import datetime, timezone
from types import SimpleNamespace

from app.services.progress import _compute_streak, filter_progress_attempts


def test_filter_progress_attempts_keeps_only_counted_attempts():
    attempts = [
        SimpleNamespace(counts_for_progress=True),
        SimpleNamespace(counts_for_progress=False),
        SimpleNamespace(counts_for_progress=True),
    ]

    filtered = filter_progress_attempts(attempts)

    assert len(filtered) == 2
    assert all(attempt.counts_for_progress for attempt in filtered)


def test_compute_streak_uses_remaining_progress_attempts():
    attempts = [
        SimpleNamespace(attempted_at=datetime(2026, 4, 22, tzinfo=timezone.utc)),
        SimpleNamespace(attempted_at=datetime(2026, 4, 21, tzinfo=timezone.utc)),
        SimpleNamespace(attempted_at=datetime(2026, 4, 19, tzinfo=timezone.utc)),
    ]

    assert _compute_streak(attempts) == 2
