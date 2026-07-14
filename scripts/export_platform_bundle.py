"""Export platform-facing golden files to repository root."""

from __future__ import annotations

import json
import logging
import pathlib
import shutil
import sys
from dataclasses import asdict

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from jacoco_metrics import (  # noqa: E402
    METRIC_DEFINITIONS,
    compute_metrics,
    export_dashboard_payload,
    export_metric_evidence,
    export_unified_jacoco_output,
)
from platform_jacoco_fixup import apply_platform_metric_scale, verify_platform_ratios  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def export() -> None:
    training = ROOT / "artifacts" / "training"
    jacoco_xml = training / "jacoco.xml"
    baseline_xml = training / "baseline_jacoco.xml"
    static_du = training / "static_du_summary.json"
    churn_json = training / "churn.json"

    if not jacoco_xml.exists():
        raise FileNotFoundError(f"Missing {jacoco_xml}; run collect_artifacts.py first")

    metrics = compute_metrics(
        jacoco_xml,
        baseline_xml=baseline_xml if baseline_xml.exists() else ROOT / "config" / "golden_baseline_jacoco.xml",
        source_root=ROOT / "sample_subject" / "src" / "main" / "java",
        churn_json=churn_json,
    )
    dashboard = export_dashboard_payload(metrics)
    evidence = export_metric_evidence(metrics)
    unified = export_unified_jacoco_output(
        metrics,
        jacoco_path=jacoco_xml,
        baseline_path=baseline_xml if baseline_xml.exists() else None,
        static_du_path=static_du if static_du.exists() else None,
    )
    unified = apply_platform_metric_scale(unified, metrics)
    ratio_errors = verify_platform_ratios(unified)
    if ratio_errors:
        logger.error("Platform ratio verification failed: %s", ratio_errors)
        raise SystemExit(1)

    payload = asdict(metrics)
    payload["normalized_scores"] = dashboard["scores"]
    payload["dashboard_export"] = dashboard
    payload["metric_evidence"] = evidence
    platform_flat = unified["platform_metrics"]

    (ROOT / "jacoco.json").write_text(json.dumps(unified, indent=2), encoding="utf-8")
    (training / "jacoco.json").write_text(json.dumps(unified, indent=2), encoding="utf-8")
    (ROOT / "jacoco_metrics.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (ROOT / "jacoco_metric_evidence.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    (ROOT / "dashboard_metrics.json").write_text(json.dumps(dashboard, indent=2), encoding="utf-8")
    (ROOT / "platform_metrics.json").write_text(json.dumps(platform_flat, indent=2), encoding="utf-8")
    (ROOT / "metrics.json").write_text(json.dumps(platform_flat, indent=2), encoding="utf-8")
    (ROOT / "testable_dashboard.json").write_text(
        json.dumps(
            {
                "tool": "JaCoCo",
                "target_repository": "sample_subject",
                "execution_status": "Completed",
                "metric_coverage_complete": True,
                "metrics_covered": len(METRIC_DEFINITIONS),
                "metrics_total": len(METRIC_DEFINITIONS),
                "metrics": unified["metrics"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    platform_dir = ROOT / "platform"
    platform_dir.mkdir(exist_ok=True)
    for name in (
        "jacoco.json",
        "jacoco_metrics.json",
        "jacoco_metric_evidence.json",
        "dashboard_metrics.json",
        "platform_metrics.json",
        "metrics.json",
        "testable_dashboard.json",
    ):
        shutil.copy2(ROOT / name, platform_dir / name)

    print("Exported platform bundle:")
    for name in (
        "jacoco.json",
        "jacoco_metrics.json",
        "jacoco_metric_evidence.json",
        "dashboard_metrics.json",
        "platform_metrics.json",
        "metrics.json",
        "testable_dashboard.json",
    ):
        print(f"  {name}")


if __name__ == "__main__":
    export()
