from __future__ import annotations

import json
import os

from code_inspector.inspectors.base import BaseInspector
from code_inspector.models import Issue, ToolResult
from code_inspector.scoring import calculate_score


class KtlintInspector(BaseInspector):
    name = "ktlint"

    async def run(self, path: str, files: list[str] | None = None, severity_weights: dict[str, float] | None = None) -> ToolResult:
        if not self.is_available():
            return ToolResult(
                tool="ktlint",
                score=0.0,
                available=False,
                error="ktlint not found. Install: brew install ktlint",
            )

        cmd = ["ktlint", "--reporter=json"]
        if files:
            cmd += files
        else:
            cmd += [os.path.join(path, "**/*.kt")]

        stdout, stderr, code = await self._run_subprocess(cmd, path)

        if not stdout.strip():
            if code == 0:
                return ToolResult(tool="ktlint", score=10.0)
            return ToolResult(
                tool="ktlint", score=0.0, error=f"ktlint failed: {stderr[:200]}"
            )

        issues = self._parse_json(stdout, path)
        total_files = len(files) if files else self._count_kt_files(path)
        score = calculate_score(issues, total_files, severity_weights)
        return ToolResult(tool="ktlint", score=score, issues=issues)

    def _parse_json(self, json_str: str, base_path: str) -> list[Issue]:
        issues: list[Issue] = []
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            return issues

        for file_entry in data:
            file_path = file_entry.get("file", "")
            if base_path and file_path.startswith(base_path):
                file_path = os.path.relpath(file_path, base_path)

            for error in file_entry.get("errors", []):
                issues.append(
                    Issue(
                        file=file_path,
                        line=error.get("line", 0),
                        column=error.get("column", 0) or None,
                        rule=error.get("rule", "unknown"),
                        message=error.get("message", ""),
                        severity="warning",
                        source="ktlint",
                    )
                )
        return issues

