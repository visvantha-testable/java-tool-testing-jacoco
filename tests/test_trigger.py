"""Verify jacoco_trigger entrypoint."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_trigger_help():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "jacoco_trigger.py"), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "33 metrics" in proc.stdout
