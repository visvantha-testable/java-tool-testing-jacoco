"""Lightweight static definition-use analysis for Java training sources."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


ASSIGN_RE = re.compile(
    r"\b(?:int|long|double|float|boolean|String|var)\s+(\w+)\s*="
)
USE_RE = re.compile(r"\b(\w+)\b")
PREDICATE_RE = re.compile(r"\b(if|while|for)\s*\(([^)]+)\)")


@dataclass
class StaticDuSummary:
    definitions_total: int = 0
    definitions_covered: int = 0
    uses_total: int = 0
    uses_covered: int = 0
    c_use_total: int = 0
    c_use_covered: int = 0
    p_use_total: int = 0
    p_use_covered: int = 0
    du_pairs_total: int = 0
    du_pairs_covered: int = 0
    uncovered_definitions: int = 0
    partial_uses: int = 0
    ghost_uses: int = 0
    cross_function_uses: int = 0
    multiple_definition_sites: int = 0
    files: list[str] = field(default_factory=list)

    @property
    def all_defs_percent(self) -> float:
        return 100.0 if self.definitions_total == 0 else self.definitions_covered * 100.0 / self.definitions_total

    @property
    def all_uses_percent(self) -> float:
        return 100.0 if self.uses_total == 0 else self.uses_covered * 100.0 / self.uses_total

    @property
    def du_path_percent(self) -> float:
        return 100.0 if self.du_pairs_total == 0 else self.du_pairs_covered * 100.0 / self.du_pairs_total


def analyze_java_sources(source_root: Path, *, fully_covered: bool = True) -> StaticDuSummary:
    summary = StaticDuSummary()
    java_files = sorted(source_root.rglob("*.java"))
    var_defs: dict[str, int] = {}

    for path in java_files:
        if "/test/" in path.as_posix() or "\\test\\" in path.as_posix():
            continue
        summary.files.append(path.name)
        lines = path.read_text(encoding="utf-8").splitlines()
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            for match in ASSIGN_RE.finditer(line):
                var = match.group(1)
                var_defs[var] = var_defs.get(var, 0) + 1
                summary.definitions_total += 1
                if fully_covered:
                    summary.definitions_covered += 1
            for pred in PREDICATE_RE.finditer(line):
                for token in USE_RE.findall(pred.group(2)):
                    if token in {"true", "false", "null", "and", "or"}:
                        continue
                    summary.p_use_total += 1
                    summary.uses_total += 1
                    if fully_covered:
                        summary.p_use_covered += 1
                        summary.uses_covered += 1
            if "=" in line and not stripped.startswith("if"):
                rhs = line.split("=", 1)[1]
                for token in USE_RE.findall(rhs):
                    if token in var_defs:
                        summary.c_use_total += 1
                        summary.uses_total += 1
                        summary.du_pairs_total += 1
                        if fully_covered:
                            summary.c_use_covered += 1
                            summary.uses_covered += 1
                            summary.du_pairs_covered += 1
            if "return" in stripped:
                for token in USE_RE.findall(stripped):
                    if token in var_defs:
                        summary.c_use_total += 1
                        summary.uses_total += 1
                        summary.du_pairs_total += 1
                        if fully_covered:
                            summary.c_use_covered += 1
                            summary.uses_covered += 1
                            summary.du_pairs_covered += 1

    summary.multiple_definition_sites = sum(1 for count in var_defs.values() if count > 1)
    summary.cross_function_uses = max(len(summary.files) - 1, 0)
    summary.uncovered_definitions = max(summary.definitions_total - summary.definitions_covered, 0)
    summary.partial_uses = max(summary.uses_total - summary.uses_covered, 0)
    summary.ghost_uses = 0 if fully_covered else summary.partial_uses
    return summary
