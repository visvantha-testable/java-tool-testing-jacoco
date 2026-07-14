"""Integration test for full JaCoCo pipeline."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_trigger_pipeline_produces_100_percent():
    subprocess.check_call(
        [sys.executable, str(ROOT / "jacoco_trigger.py"), "--skip-verify"],
        cwd=ROOT,
    )
    payload = json.loads((ROOT / "jacoco.json").read_text(encoding="utf-8"))
    assert payload["metrics_total"] == 33
    assert payload["metrics_covered"] == 33
    assert all(int(row["score"]) == 100 for row in payload["metrics"])
