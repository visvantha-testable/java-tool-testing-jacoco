"""Tests for JaCoCo metric derivation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def artifacts_ready():
    training = ROOT / "artifacts" / "training"
    if not (training / "jacoco.xml").exists():
        import subprocess
        import sys

        subprocess.check_call([sys.executable, str(ROOT / "scripts" / "collect_artifacts.py")], cwd=ROOT)
        subprocess.check_call([sys.executable, str(ROOT / "scripts" / "export_platform_bundle.py")], cwd=ROOT)
    return training


def test_metric_definitions_count():
    from jacoco_metrics import METRIC_DEFINITIONS

    assert len(METRIC_DEFINITIONS) == 33


def test_all_metrics_score_100(artifacts_ready):
    from jacoco_metrics import compute_metrics, compute_normalized_scores

    metrics = compute_metrics(
        artifacts_ready / "jacoco.xml",
        baseline_xml=artifacts_ready / "baseline_jacoco.xml",
        source_root=ROOT / "sample_subject" / "src" / "main" / "java",
        churn_json=artifacts_ready / "churn.json",
    )
    scores = compute_normalized_scores(metrics)
    assert len(scores) == 33
    assert all(value >= 100.0 for value in scores.values())


def test_jacoco_json_complete(artifacts_ready):
    jacoco_json = ROOT / "jacoco.json"
    if not jacoco_json.exists():
        pytest.skip("jacoco.json not exported yet")
    payload = json.loads(jacoco_json.read_text(encoding="utf-8"))
    assert payload["metrics_total"] == 33
    assert payload["metrics_covered"] == 33
    assert payload["metric_coverage_complete"] is True
    assert all(row["covered"] == "yes" for row in payload["metrics"])
    assert all(int(row["score"]) >= 100 for row in payload["metrics"])
