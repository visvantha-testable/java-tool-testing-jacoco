"""Parse JaCoCo XML and extract coverage counters."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class JacocoCounters:
    line_missed: int = 0
    line_covered: int = 0
    branch_missed: int = 0
    branch_covered: int = 0
    instruction_missed: int = 0
    instruction_covered: int = 0
    method_missed: int = 0
    method_covered: int = 0
    complexity_missed: int = 0
    complexity_covered: int = 0
    ghost_lines: int = 0
    partial_branch_lines: int = 0
    source_files: list[str] = field(default_factory=list)
    session_id: str = ""
    session_start: str = ""

    @property
    def line_total(self) -> int:
        return self.line_missed + self.line_covered

    @property
    def branch_total(self) -> int:
        return self.branch_missed + self.branch_covered

    @property
    def line_percent(self) -> float:
        return 100.0 if self.line_total == 0 else self.line_covered * 100.0 / self.line_total

    @property
    def branch_percent(self) -> float:
        return 100.0 if self.branch_total == 0 else self.branch_covered * 100.0 / self.branch_total

    @property
    def instruction_percent(self) -> float:
        total = self.instruction_missed + self.instruction_covered
        return 100.0 if total == 0 else self.instruction_covered * 100.0 / total


def _counter_value(node: ET.Element | None, counter_type: str) -> tuple[int, int]:
    if node is None:
        return 0, 0
    for counter in node.findall("counter"):
        if counter.get("type") == counter_type:
            return int(counter.get("missed", 0)), int(counter.get("covered", 0))
    return 0, 0


def parse_jacoco_xml(path: Path) -> JacocoCounters:
    root = ET.parse(path).getroot()
    counters = JacocoCounters()

    session = root.find("sessioninfo")
    if session is not None:
        counters.session_id = session.get("id", "")
        counters.session_start = session.get("start", "")

    missed, covered = _counter_value(root, "LINE")
    counters.line_missed, counters.line_covered = missed, covered
    missed, covered = _counter_value(root, "BRANCH")
    counters.branch_missed, counters.branch_covered = missed, covered
    missed, covered = _counter_value(root, "INSTRUCTION")
    counters.instruction_missed, counters.instruction_covered = missed, covered
    missed, covered = _counter_value(root, "METHOD")
    counters.method_missed, counters.method_covered = missed, covered
    missed, covered = _counter_value(root, "COMPLEXITY")
    counters.complexity_missed, counters.complexity_covered = missed, covered

    for package in root.findall("package"):
        for sourcefile in package.findall("sourcefile"):
            name = sourcefile.get("name", "")
            if name:
                counters.source_files.append(name)
            for line in sourcefile.findall("line"):
                mi = int(line.get("mi", 0))
                ci = int(line.get("ci", 0))
                mb = int(line.get("mb", 0))
                cb = int(line.get("cb", 0))
                if mi > 0 and ci == 0:
                    counters.ghost_lines += 1
                if mb > 0 and cb > 0 and cb < mb:
                    counters.partial_branch_lines += 1

    return counters


def coverage_ratio(counters: JacocoCounters) -> dict[str, float]:
    return {
        "line_percent": round(counters.line_percent, 2),
        "branch_percent": round(counters.branch_percent, 2),
        "instruction_percent": round(counters.instruction_percent, 2),
        "path_coverage_percent": round(counters.branch_percent, 2),
    }
