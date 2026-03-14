from __future__ import annotations

import os
import tempfile
import xml.etree.ElementTree as ET

from code_inspector.inspectors.base import BaseInspector
from code_inspector.models import Issue, ToolResult
from code_inspector.scoring import calculate_score

SEVERITY_MAP = {
    "error": "error",
    "warning": "warning",
    "info": "info",
    "style": "info",
}


class DetektInspector(BaseInspector):
    name = "detekt-cli"

    def _has_gradle_detekt(self, path: str) -> bool:
        gradlew = os.path.join(path, "gradlew")
        return os.path.isfile(gradlew) and os.access(gradlew, os.X_OK)

    async def run(self, path: str, files: list[str] | None = None, severity_weights: dict[str, float] | None = None) -> ToolResult:
        if not self.is_available() and not self._has_gradle_detekt(path):
            return ToolResult(
                tool="detekt",
                score=0.0,
                available=False,
                error="detekt-cli not found. Install: brew install detekt",
            )

        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp:
            report_path = tmp.name

        try:
            if self.is_available():
                cmd = ["detekt-cli", "--report", f"xml:{report_path}"]
                if files:
                    cmd += ["--input", ",".join(files)]
                else:
                    cmd += ["--input", path]
            else:
                cmd = [os.path.join(path, "gradlew"), "detekt"]

            stdout, stderr, code = await self._run_subprocess(cmd, path)

            if not os.path.isfile(report_path) or os.path.getsize(report_path) == 0:
                if code == 0:
                    return ToolResult(tool="detekt", score=10.0)
                return ToolResult(
                    tool="detekt", score=0.0, error=f"detekt failed: {stderr[:200]}"
                )

            issues = self._parse_xml(report_path, path)
            total_files = len(files) if files else self._count_kt_files(path)
            score = calculate_score(issues, total_files, severity_weights)
            return ToolResult(tool="detekt", score=score, issues=issues)
        finally:
            if os.path.isfile(report_path):
                os.unlink(report_path)

    def _parse_xml(self, xml_path: str, base_path: str) -> list[Issue]:
        issues: list[Issue] = []
        try:
            tree = ET.parse(xml_path)
        except ET.ParseError:
            return issues

        root = tree.getroot()
        for file_elem in root.findall(".//file"):
            file_path = file_elem.get("name", "")
            if base_path and file_path.startswith(base_path):
                file_path = os.path.relpath(file_path, base_path)

            for error_elem in file_elem.findall("error"):
                severity_raw = error_elem.get("severity", "warning")
                severity = SEVERITY_MAP.get(severity_raw, "warning")
                issues.append(
                    Issue(
                        file=file_path,
                        line=int(error_elem.get("line", "0")),
                        column=int(error_elem.get("column", "0")) or None,
                        rule=error_elem.get("source", "unknown"),
                        message=error_elem.get("message", ""),
                        severity=severity,
                        source="detekt",
                    )
                )
        return issues

