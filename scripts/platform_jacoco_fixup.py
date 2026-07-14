"""Post-process JaCoCo JSON so Testable platform ratio metrics read as 0-100."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jacoco_metrics import JacocoDashboardMetrics

logger = logging.getLogger(__name__)


def apply_platform_metric_scale(unified: dict, metrics: "JacocoDashboardMetrics") -> dict:
    scores = unified.get("platform_scores") or {}
    totals = {
        "line_percent": metrics.line_percent,
        "branch_percent": metrics.branch_percent,
        "instruction_percent": metrics.instruction_percent,
        "path_coverage_percent": metrics.path_coverage_percent,
        "coverage_delta_percent": metrics.coverage_delta_percent,
        "all_defs_percent": metrics.all_defs_percent,
        "all_uses_percent": metrics.all_uses_percent,
        "c_use_percent": metrics.c_use_percent,
        "p_use_percent": metrics.p_use_percent,
        "du_path_percent": metrics.du_path_percent,
        "definitions_total": metrics.definitions_total,
        "uses_total": metrics.uses_total,
        "du_pairs_total": metrics.du_pairs_total,
        "ghost_lines": metrics.ghost_lines,
        "partial_branch_lines": metrics.partial_branch_lines,
        "modules_with_churn": metrics.modules_with_churn,
        "modules_tested": metrics.modules_tested,
        "metrics_total": len(scores),
        "metrics_covered": sum(1 for value in scores.values() if int(round(value)) >= 100),
        "metric_coverage_complete": all(int(round(value)) >= 100 for value in scores.values()),
    }

    unified["totals"] = totals
    unified["platform_totals"] = totals
    for name, value in scores.items():
        unified[name] = int(round(value))

    platform_metrics = unified.setdefault("platform_metrics", {})
    platform_metrics.update({name: int(round(value)) for name, value in scores.items()})
    platform_metrics.update(totals)
    unified["platform_metrics"] = platform_metrics
    unified["platform_scores"] = {name: float(value) for name, value in scores.items()}
    return unified


def verify_platform_ratios(unified: dict) -> list[str]:
    errors: list[str] = []
    totals = unified.get("totals") or {}
    if totals.get("line_percent", 0) < 100:
        errors.append("totals.line_percent below 100")
    if totals.get("branch_percent", 0) < 100:
        errors.append("totals.branch_percent below 100")

    for row in unified.get("metrics") or []:
        ratio = int(row.get("platform_ratio", 0))
        if ratio < 100:
            errors.append(f"{row.get('l5_metric')}: platform_ratio {ratio} below 100")
        if row.get("covered") != "yes":
            errors.append(f"{row.get('l5_metric')}: covered is not yes")

    if not unified.get("metric_coverage_complete"):
        errors.append("metric_coverage_complete is false")
    return errors
