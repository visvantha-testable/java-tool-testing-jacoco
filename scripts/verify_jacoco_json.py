"""Verify unified jacoco.json has all 33 metrics covered with yes + 100/100."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from jacoco_metrics import METRIC_DEFINITIONS


def verify(path: pathlib.Path) -> int:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    errors: list[str] = []
    expected = len(METRIC_DEFINITIONS)

    if not payload.get("output_complete"):
        errors.append("output_complete is not true")
    if not payload.get("metric_coverage_complete"):
        errors.append("metric_coverage_complete is not true")
    if payload.get("metrics_covered") != expected:
        errors.append(f"metrics_covered is {payload.get('metrics_covered')} not {expected}")
    if payload.get("metrics_total") != expected:
        errors.append(f"metrics_total is {payload.get('metrics_total')} not {expected}")

    metrics = payload.get("metrics") or []
    if len(metrics) != expected:
        errors.append(f"expected {expected} metric rows, got {len(metrics)}")

    for row in metrics:
        name = row.get("l5_metric", "?")
        if row.get("covered") != "yes":
            errors.append(f"{name}: covered is not 'yes'")
        if int(row.get("score", 0)) < 100:
            errors.append(f"{name}: score {row.get('score')} below 100")
        if row.get("result") != "PASS":
            errors.append(f"{name}: result is not PASS")
        if not row.get("raw_sources_present"):
            errors.append(f"{name}: raw_sources_present is false")
        if not row.get("raw_parameters"):
            errors.append(f"{name}: raw_parameters missing")
        if int(row.get("coverage_percent", 0)) < 100:
            errors.append(f"{name}: coverage_percent below 100")
        if int(row.get("platform_ratio", 0)) < 100:
            errors.append(f"{name}: platform_ratio below 100")

    totals = payload.get("totals") or payload.get("platform_totals") or {}
    if not totals:
        errors.append("missing totals block")
    else:
        if totals.get("line_percent", 0) < 100:
            errors.append("totals.line_percent below 100")
        if totals.get("branch_percent", 0) < 100:
            errors.append("totals.branch_percent below 100")

    supplemental = payload.get("supplemental_raw_data") or {}
    if "jacoco_xml" not in supplemental:
        errors.append("missing supplemental_raw_data.jacoco_xml")

    if errors:
        print("FAIL: jacoco.json incomplete:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"PASS: jacoco.json has all {expected} JaCoCo metrics covered=yes with 100/100 score")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jacoco-json", type=pathlib.Path, default=pathlib.Path("jacoco.json"))
    args = parser.parse_args()
    return verify(args.jacoco_json)


if __name__ == "__main__":
    raise SystemExit(main())
