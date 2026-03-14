from __future__ import annotations

import asyncio
import os

from fastmcp import FastMCP

from code_inspector.inspectors.android_lint import AndroidLintInspector
from code_inspector.inspectors.detekt import DetektInspector
from code_inspector.inspectors.ktlint import KtlintInspector
from code_inspector.models import InspectionResult, ToolResult

mcp = FastMCP("code-inspector")

INSPECTORS = [
    DetektInspector(),
    KtlintInspector(),
    AndroidLintInspector(),
]


@mcp.tool
async def inspect(
    path: str = ".",
    scope: str = "changed",
    fix: bool = False,
    threshold: float = 7.0,
) -> dict:
    """Run code quality inspection using detekt, ktlint, and Android Lint.

    Args:
        path: Target Android project path (default: current directory)
        scope: "changed" for git diff only, "all" for entire project
        fix: If true, include actionable fix suggestions
        threshold: Pass/fail threshold on 10-point scale (default: 7.0)
    """
    path = os.path.abspath(path)

    files = None
    if scope == "changed":
        files = INSPECTORS[0]._get_changed_files(path, [".kt", ".kts"])

    results: list[ToolResult] = await asyncio.gather(
        *[inspector.run(path, files) for inspector in INSPECTORS]
    )

    available_results = [r for r in results if r.available]
    if available_results:
        overall = round(
            sum(r.score for r in available_results) / len(available_results), 2
        )
    else:
        overall = 0.0

    passed = overall >= threshold

    lines = []
    for r in results:
        status = "✅" if r.score >= threshold else "❌"
        if not r.available:
            status = "⚠️"
            lines.append(f"{r.tool}: {status} (not installed)")
        else:
            lines.append(f"{r.tool}: {r.score}/10 {status}")

    lines.append(f"overall: {overall}/10 {'PASS ✅' if passed else 'FAIL ❌'}")

    summary = "\n".join(lines)

    result = InspectionResult(
        path=path,
        scope=scope,
        overall_score=overall,
        passed=passed,
        threshold=threshold,
        tool_results=results,
        summary=summary,
    )

    output = result.model_dump()

    if fix and not passed:
        suggestions = _generate_fix_suggestions(results)
        output["fix_suggestions"] = suggestions

    return output


def _generate_fix_suggestions(results: list[ToolResult]) -> list[str]:
    suggestions: list[str] = []
    for r in results:
        if not r.available or not r.issues:
            continue
        by_rule: dict[str, int] = {}
        for issue in r.issues:
            by_rule[issue.rule] = by_rule.get(issue.rule, 0) + 1
        for rule, count in sorted(by_rule.items(), key=lambda x: -x[1]):
            sample = next(i for i in r.issues if i.rule == rule)
            suggestions.append(
                f"[{r.tool}] {rule} ({count}x): {sample.message} — {sample.file}:{sample.line}"
            )
    return suggestions


def main():
    mcp.run()


if __name__ == "__main__":
    main()
