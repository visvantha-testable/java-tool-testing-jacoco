"""Collect JaCoCo artifacts from Maven or synthesize golden training XML."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "sample_subject"
OUTPUT = ROOT / "artifacts" / "training"


def _maven_available() -> bool:
    try:
        subprocess.run(["mvn", "-version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _collect_with_maven(output_dir: Path) -> Path:
    subprocess.check_call(["mvn", "clean", "test", "jacoco:report"], cwd=SAMPLE)
    jacoco_xml = SAMPLE / "target" / "site" / "jacoco" / "jacoco.xml"
    if not jacoco_xml.exists():
        raise FileNotFoundError(f"Missing JaCoCo report: {jacoco_xml}")
    output_dir.mkdir(parents=True, exist_ok=True)
    dest = output_dir / "jacoco.xml"
    shutil.copy2(jacoco_xml, dest)
    return dest


def _collect_with_synthesis(output_dir: Path) -> Path:
    subprocess.check_call(
        [sys.executable, str(ROOT / "scripts" / "synthesize_training_artifacts.py"), "--output", str(output_dir / "jacoco.xml")],
        cwd=ROOT,
    )
    return output_dir / "jacoco.xml"


def collect(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    if _maven_available():
        print("Using Maven + JaCoCo to collect artifacts")
        jacoco_xml = _collect_with_maven(output_dir)
    else:
        print("Maven unavailable — synthesizing golden JaCoCo XML from Java sources")
        jacoco_xml = _collect_with_synthesis(output_dir)

    baseline_src = ROOT / "config" / "golden_baseline_jacoco.xml"
    if baseline_src.exists():
        shutil.copy2(baseline_src, output_dir / "baseline_jacoco.xml")

    churn_src = output_dir / "churn.json"
    if not churn_src.exists():
        churn_src.write_text(
            json.dumps(
                {
                    "modules_with_churn": 3,
                    "modules_tested": 3,
                    "files": ["OrderService.java", "PaymentValidator.java", "DataFlowSample.java"],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    sys.path.insert(0, str(ROOT))
    from static_du_analysis import analyze_java_sources  # noqa: E402

    summary = analyze_java_sources(SAMPLE / "src" / "main" / "java", fully_covered=True)
    (output_dir / "static_du_summary.json").write_text(json.dumps(summary.__dict__, indent=2), encoding="utf-8")
    print(f"Collected JaCoCo artifacts in {output_dir}")
    return jacoco_xml


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    collect(args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
