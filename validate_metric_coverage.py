"""Validate that all 33 JaCoCo dashboard metrics are fully covered."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from jacoco_metrics import METRIC_DEFINITIONS, compute_metrics, compute_normalized_scores  # noqa: E402


def load_config(config_path: pathlib.Path) -> list[dict]:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return data["metrics"]


def validate(
    *,
    config_path: pathlib.Path,
    artifacts_dir: pathlib.Path,
    metrics_json: pathlib.Path | None = None,
) -> tuple[bool, list[str]]:
    entries = load_config(config_path)
    errors: list[str] = []

    jacoco_xml = artifacts_dir / "jacoco.xml"
    baseline_xml = artifacts_dir / "baseline_jacoco.xml"
    churn_json = artifacts_dir / "churn.json"

    if metrics_json and metrics_json.exists():
        payload = json.loads(metrics_json.read_text(encoding="utf-8"))
        scores = payload.get("normalized_scores") or {}
    else:
        computed = compute_metrics(
            jacoco_xml,
            baseline_xml=baseline_xml if baseline_xml.exists() else ROOT / "config" / "golden_baseline_jacoco.xml",
            source_root=ROOT / "sample_subject" / "src" / "main" / "java",
            churn_json=churn_json,
        )
        scores = compute_normalized_scores(computed)

    for entry in entries:
        name = entry["normalized_score_key"]
        for artifact in entry.get("required_artifacts", []):
            path = ROOT / artifact
            if not path.exists():
                errors.append(f"{name}: missing artifact {artifact}")
            elif path.stat().st_size == 0:
                errors.append(f"{name}: empty artifact {artifact}")
        if name not in scores:
            errors.append(f"{name}: missing normalized score")
            continue
        if float(scores[name]) < 100.0:
            errors.append(f"{name}: score {scores[name]} is below 100/100")

    if not jacoco_xml.exists():
        errors.append("missing artifacts/training/jacoco.xml")

    if len(entries) != len(METRIC_DEFINITIONS):
        errors.append(f"config metrics count {len(entries)} != {len(METRIC_DEFINITIONS)}")

    return len(errors) == 0, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=pathlib.Path, default=ROOT / "config" / "metric_coverage.json")
    parser.add_argument("--artifacts-dir", type=pathlib.Path, default=ROOT / "artifacts" / "training")
    parser.add_argument("--metrics-json", type=pathlib.Path, default=None)
    args = parser.parse_args()

    ok, errors = validate(
        config_path=args.config,
        artifacts_dir=args.artifacts_dir,
        metrics_json=args.metrics_json,
    )
    if ok:
        print(f"All {len(METRIC_DEFINITIONS)} JaCoCo metrics are covered with 100/100 scores.")
        return 0

    print("Metric coverage validation failed:", file=sys.stderr)
    for err in errors:
        print(f"  - {err}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
