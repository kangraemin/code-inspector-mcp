from __future__ import annotations

import glob
import os
import xml.etree.ElementTree as ET


def analyze_coverage(
    project_path: str, min_percent: float = 80.0
) -> dict:
    """Parse JaCoCo XML reports and calculate line coverage.

    Args:
        project_path: Android project root path
        min_percent: Minimum coverage percentage to pass
    """
    report_path = _find_jacoco_report(project_path)
    if not report_path:
        return {
            "available": False,
            "error": "JaCoCo report not found. Run tests first: ./gradlew testDebugUnitTest jacocoTestReport",
            "coverage_percent": 0.0,
            "passed": False,
            "min_percent": min_percent,
        }

    covered, missed = _parse_jacoco_xml(report_path)
    total = covered + missed
    pct = round((covered / total * 100) if total > 0 else 0, 2)

    return {
        "available": True,
        "coverage_percent": pct,
        "covered_lines": covered,
        "missed_lines": missed,
        "total_lines": total,
        "passed": pct >= min_percent,
        "min_percent": min_percent,
        "report_path": report_path,
    }


def _find_jacoco_report(project_path: str) -> str | None:
    patterns = [
        os.path.join(project_path, "**", "jacocoTestReport.xml"),
        os.path.join(project_path, "**", "jacoco", "**", "*.xml"),
        os.path.join(project_path, "**", "build", "reports", "jacoco", "**", "*.xml"),
    ]
    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            return matches[0]
    return None


def _parse_jacoco_xml(xml_path: str) -> tuple[int, int]:
    covered = 0
    missed = 0
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError:
        return 0, 0

    root = tree.getroot()
    for counter in root.findall(".//counter"):
        if counter.get("type") == "LINE":
            covered += int(counter.get("covered", "0"))
            missed += int(counter.get("missed", "0"))

    return covered, missed
