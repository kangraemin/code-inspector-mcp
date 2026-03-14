from __future__ import annotations

import glob
import os
import xml.etree.ElementTree as ET

from code_inspector.inspectors.base import BaseInspector
from code_inspector.models import Issue, ToolResult
from code_inspector.scoring import calculate_score

SEVERITY_MAP = {
    "Fatal": "error",
    "Error": "error",
    "Warning": "warning",
    "Information": "info",
    "Ignore": "info",
}


class AndroidLintInspector(BaseInspector):
    name = "gradlew"

    def is_available(self) -> bool:
        return False

    def _has_gradlew(self, path: str) -> bool:
        gradlew = os.path.join(path, "gradlew")
        return os.path.isfile(gradlew) and os.access(gradlew, os.X_OK)

    async def run(self, path: str, files: list[str] | None = None, severity_weights: dict[str, float] | None = None) -> ToolResult:
        if not self._has_gradlew(path):
            return ToolResult(
                tool="android_lint",
                score=0.0,
                available=False,
                error="gradlew not found. Run from Android project root.",
            )

        gradlew = os.path.join(path, "gradlew")
        stdout, stderr, code = await self._run_subprocess(
            [gradlew, "lintDebug"], path, timeout=300
        )

        report_path = self._find_report(path)
        if not report_path:
            if code == 0:
                return ToolResult(tool="android_lint", score=10.0)
            return ToolResult(
                tool="android_lint",
                score=0.0,
                error=f"Android Lint failed: {stderr[:200]}",
            )

        all_issues = self._parse_xml(report_path, path)

        if files:
            all_issues = [i for i in all_issues if i.file in files]

        total_files = len(files) if files else self._count_kt_files(path)
        score = calculate_score(all_issues, total_files, severity_weights)
        return ToolResult(tool="android_lint", score=score, issues=all_issues)

    def _find_report(self, path: str) -> str | None:
        patterns = [
            os.path.join(path, "**", "build", "reports", "lint-results*.xml"),
        ]
        for pattern in patterns:
            matches = glob.glob(pattern, recursive=True)
            if matches:
                return matches[0]
        return None

    def _parse_xml(self, xml_path: str, base_path: str) -> list[Issue]:
        issues: list[Issue] = []
        try:
            tree = ET.parse(xml_path)
        except ET.ParseError:
            return issues

        root = tree.getroot()
        for issue_elem in root.findall("issue"):
            severity_raw = issue_elem.get("severity", "Warning")
            severity = SEVERITY_MAP.get(severity_raw, "warning")
            rule = issue_elem.get("id", "unknown")
            message = issue_elem.get("message", "")

            for loc in issue_elem.findall("location"):
                file_path = loc.get("file", "")
                if base_path and file_path.startswith(base_path):
                    file_path = os.path.relpath(file_path, base_path)

                issues.append(
                    Issue(
                        file=file_path,
                        line=int(loc.get("line", "0")),
                        column=int(loc.get("column", "0")) or None,
                        rule=rule,
                        message=message,
                        severity=severity,
                        source="android_lint",
                    )
                )
        return issues

