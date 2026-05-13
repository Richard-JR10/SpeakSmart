from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.services.pronunciation_benchmark import (
    load_benchmark_cases,
    run_ai_pronunciation_benchmark,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run objective AI-led Japanese pronunciation benchmark cases."
    )
    parser.add_argument("cases", help="Path to benchmark cases JSON")
    parser.add_argument(
        "--output",
        help="Optional path for the benchmark report JSON",
    )
    args = parser.parse_args()

    cases = load_benchmark_cases(args.cases)
    report = run_ai_pronunciation_benchmark(cases).to_dict()
    report_json = json.dumps(report, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(report_json, encoding="utf-8")
    else:
        print(report_json)


if __name__ == "__main__":
    main()
