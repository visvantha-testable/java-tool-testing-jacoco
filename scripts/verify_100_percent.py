"""Verify all dashboard metrics score 100/100."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from jacoco_metrics import METRIC_DEFINITIONS  # noqa: E402


def verify(metrics_json: pathlib.Path, dashboard_json: pathlib.Path) -> int:
    errors: list[str] = []
    metrics_payload = json.loads(metrics_json.read_text(encoding="utf-8-sig"))
    dashboard_payload = json.loads(dashboard_json.read_text(encoding="utf-8-sig"))

    scores = metrics_payload.get("normalized_scores") or dashboard_payload.get("scores") or {}
    for item in METRIC_DEFINITIONS:
        key = item["key"]
        if key not in scores:
            errors.append(f"missing score for {key}")
            continue
        if float(scores[key]) < 100.0:
            errors.append(f"{key}: {scores[key]} below 100")

    if not dashboard_payload.get("metric_coverage_complete"):
        errors.append("dashboard metric_coverage_complete is false")
    if not dashboard_payload.get("all_scores_100"):
        errors.append("dashboard all_scores_100 is false")

    if errors:
        print("FAIL: not all metrics at 100/100:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"PASS: all {len(METRIC_DEFINITIONS)} metrics at 100/100")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics-json", type=pathlib.Path, default=ROOT / "jacoco_metrics.json")
    parser.add_argument("--dashboard-json", type=pathlib.Path, default=ROOT / "dashboard_metrics.json")
    args = parser.parse_args()
    return verify(args.metrics_json, args.dashboard_json)


if __name__ == "__main__":
    raise SystemExit(main())
