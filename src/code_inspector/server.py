from __future__ import annotations

import asyncio
import os
from pathlib import PurePath

from fastmcp import FastMCP

from code_inspector.inspectors.android_lint import AndroidLintInspector
from code_inspector.inspectors.detekt import DetektInspector
from code_inspector.inspectors.ktlint import KtlintInspector
from code_inspector.config import (
    CONFIG_FILENAME,
    CodeInspectorConfig,
    deep_merge,
    load_config,
    save_config,
)
from code_inspector.metrics.complexity import analyze_complexity
from code_inspector.metrics.coverage import analyze_coverage
from code_inspector.metrics.duplication import analyze_duplication
from code_inspector.models import InspectionResult, ToolResult
from code_inspector.scoring import calculate_score

mcp = FastMCP("code-inspector")

SKIP_DIRS = {"build", "generated", ".gradle", ".idea", "__pycache__", "node_modules"}
CONFIG_FILE_NAMES = [
    "detekt.yml", "detekt.yaml",
    ".editorconfig",
    "build.gradle", "build.gradle.kts",
    "settings.gradle", "settings.gradle.kts",
    ".code-inspector.json",
]
ARCH_PATTERNS = {
    "has_viewmodel": "ViewModel",
    "has_repository": "Repository",
    "has_usecase": "UseCase",
    "has_contract": ("Contract", "UiState"),
    "has_compose": "androidx.compose",
    "has_hilt": "dagger.hilt",
    "has_coroutines": "kotlinx.coroutines",
    "has_flow": "kotlinx.coroutines.flow",
}

INSPECTORS = [
    DetektInspector(),
    KtlintInspector(),
    AndroidLintInspector(),
]


INSPECTOR_NAME_MAP = {
    "detekt": 0,
    "ktlint": 1,
    "android_lint": 2,
}


@mcp.tool
async def inspect(
    path: str = ".",
    scope: str = "changed",
    fix: bool = False,
    threshold: float | None = None,
) -> dict:
    """Run code quality inspection using detekt, ktlint, and Android Lint.

    Args:
        path: Target Android project path (default: current directory)
        scope: "changed" for git diff only, "all" for entire project
        fix: If true, include actionable fix suggestions
        threshold: Pass/fail threshold on 10-point scale (uses config or 7.0)
    """
    path = os.path.abspath(path)

    cfg = load_config(path)
    if cfg is None:
        cfg = CodeInspectorConfig()

    if threshold is None:
        threshold = cfg.threshold

    default_inspector_cfg = CodeInspectorConfig().inspectors["detekt"]
    tool_name_map = {"detekt-cli": "detekt", "ktlint": "ktlint", "gradlew": "android_lint"}

    enabled_inspectors = [
        insp
        for insp in INSPECTORS
        if cfg.inspectors.get(tool_name_map.get(insp.name, insp.name), default_inspector_cfg).enabled
    ]

    files = None
    if scope == "changed" and enabled_inspectors:
        files = enabled_inspectors[0]._get_changed_files(path, [".kt", ".kts"])

    results: list[ToolResult] = await asyncio.gather(
        *[inspector.run(path, files, cfg.severity_weights) for inspector in enabled_inspectors]
    )

    # ignore 패턴으로 이슈 필터링
    if cfg.ignore:
        for r in results:
            if r.available and r.issues:
                original_count = len(r.issues)
                r.issues = [
                    issue for issue in r.issues
                    if not _should_ignore(issue.file, cfg.ignore)
                ]
                if len(r.issues) != original_count:
                    total = len(files) if files else enabled_inspectors[0]._count_kt_files(path)
                    r.score = calculate_score(r.issues, total, cfg.severity_weights)

    available_results = [r for r in results if r.available]
    if available_results:
        total_weight = 0.0
        weighted_sum = 0.0
        for r in available_results:
            tool_key = r.tool
            inspector_cfg = cfg.inspectors.get(tool_key)
            w = inspector_cfg.weight if inspector_cfg else 1.0
            weighted_sum += r.score * w
            total_weight += w
        overall = round(weighted_sum / total_weight, 2) if total_weight > 0 else 0.0
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

    # Metrics 분석
    metrics_results = {}
    kt_files_for_metrics = None

    if cfg.metrics.complexity.enabled or cfg.metrics.duplication.enabled:
        kt_files_for_metrics = _collect_kt_files(path, files, cfg.ignore)

    if cfg.metrics.complexity.enabled and kt_files_for_metrics:
        complexity_violations = []
        for fi in kt_files_for_metrics:
            cr = analyze_complexity(
                fi["content"], fi["path"], cfg.metrics.complexity.max_per_function
            )
            if cr["violations"]:
                complexity_violations.append(cr)
        metrics_results["complexity"] = {
            "files_analyzed": len(kt_files_for_metrics),
            "violations": complexity_violations,
        }

    if cfg.metrics.duplication.enabled and kt_files_for_metrics:
        metrics_results["duplication"] = analyze_duplication(kt_files_for_metrics)

    if cfg.metrics.coverage.enabled:
        metrics_results["coverage"] = analyze_coverage(
            path, cfg.metrics.coverage.min_percent
        )

    # Metrics summary
    if metrics_results:
        if "complexity" in metrics_results:
            v_count = len(metrics_results["complexity"]["violations"])
            lines.append(f"complexity: {v_count} violation(s)")
        if "duplication" in metrics_results:
            dup_pct = metrics_results["duplication"]["duplication_percentage"]
            lines.append(f"duplication: {dup_pct}%")
        if "coverage" in metrics_results:
            cov = metrics_results["coverage"]
            if cov.get("available"):
                lines.append(f"coverage: {cov['coverage_percent']}%")
            else:
                lines.append("coverage: N/A")

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

    if metrics_results:
        output["metrics"] = metrics_results

    if fix and not passed:
        suggestions = _generate_fix_suggestions(results)
        output["fix_suggestions"] = suggestions

    return output


@mcp.tool
async def inspect_init(path: str = ".") -> dict:
    """Collect all Kotlin files and project metadata for config generation.

    Reads ALL .kt files in the project (no upper limit) plus config files.
    Returns file contents and architecture hints for Claude to analyze
    and generate .code-inspector.json.

    Args:
        path: Target Android project path (default: current directory)
    """
    path = os.path.abspath(path)

    kt_files: list[dict] = []
    config_files: dict[str, str] = {}
    architecture_hints: dict[str, bool] = {k: False for k in ARCH_PATTERNS}
    module_dirs: list[str] = []

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        rel_root = os.path.relpath(root, path)

        for fname in files:
            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, path)

            if fname in ("build.gradle", "build.gradle.kts") and rel_root != ".":
                module_dirs.append(rel_root)

            if root == path and fname in CONFIG_FILE_NAMES:
                try:
                    with open(fpath, errors="replace") as f:
                        config_files[fname] = f.read()
                except OSError:
                    pass

            if fname.endswith((".kt", ".kts")) and not fname.endswith(
                (".gradle.kts", "settings.gradle.kts")
            ):
                content = None
                lines = 0
                skipped = False
                try:
                    with open(fpath, errors="replace") as f:
                        content = f.read()
                    lines = content.count("\n") + 1
                    if len(content) > 50000:
                        content = None
                        skipped = True
                except OSError:
                    skipped = True

                kt_files.append({
                    "path": rel_path,
                    "content": content,
                    "lines": lines,
                    "skipped": skipped,
                })

                check_text = content or fname
                for hint_key, pattern in ARCH_PATTERNS.items():
                    if isinstance(pattern, tuple):
                        if any(p in fname or (content and p in content) for p in pattern):
                            architecture_hints[hint_key] = True
                    elif pattern in fname or (content and pattern in content):
                        architecture_hints[hint_key] = True

    existing_config = None
    cfg = load_config(path)
    if cfg:
        existing_config = cfg.model_dump()

    total_lines = sum(f["lines"] for f in kt_files)

    return {
        "kt_files": kt_files,
        "config_files": config_files,
        "project_info": {
            "total_kt_files": len(kt_files),
            "total_lines": total_lines,
            "module_structure": module_dirs,
        },
        "architecture_hints": architecture_hints,
        "existing_config": existing_config,
    }


@mcp.tool
async def inspect_config(
    path: str = ".",
    action: str = "read",
    updates: dict | None = None,
) -> dict:
    """Read, update, or reset the .code-inspector.json config file.

    Args:
        path: Target project path (default: current directory)
        action: "read" to view config, "update" to modify, "reset" to restore defaults
        updates: Partial config dict to deep-merge (only for action="update")
    """
    path = os.path.abspath(path)
    config_path = os.path.join(path, CONFIG_FILENAME)

    if action == "reset":
        if os.path.isfile(config_path):
            os.remove(config_path)
        defaults = CodeInspectorConfig()
        return {
            "config": defaults.model_dump(),
            "path": config_path,
            "action_taken": "reset to defaults (file removed)",
        }

    if action == "update" and updates:
        existing = load_config(path)
        if existing:
            merged = deep_merge(existing.model_dump(), updates)
        else:
            merged = deep_merge(CodeInspectorConfig().model_dump(), updates)
        new_config = CodeInspectorConfig(**merged)
        saved_path = save_config(path, new_config)
        return {
            "config": new_config.model_dump(),
            "path": saved_path,
            "action_taken": "updated",
        }

    # read
    existing = load_config(path)
    if existing:
        return {
            "config": existing.model_dump(),
            "path": config_path,
            "action_taken": "read (from file)",
        }
    defaults = CodeInspectorConfig()
    return {
        "config": defaults.model_dump(),
        "path": config_path,
        "action_taken": "read (defaults, no file exists)",
    }


def _should_ignore(file_path: str, patterns: list[str]) -> bool:
    p = PurePath(file_path)
    return any(p.full_match(pat) for pat in patterns)


def _collect_kt_files(
    path: str,
    changed_files: list[str] | None,
    ignore_patterns: list[str],
) -> list[dict]:
    result = []
    if changed_files:
        for rel_path in changed_files:
            if _should_ignore(rel_path, ignore_patterns):
                continue
            abs_path = os.path.join(path, rel_path)
            try:
                with open(abs_path, errors="replace") as f:
                    content = f.read()
                result.append({"path": rel_path, "content": content})
            except OSError:
                pass
    else:
        for root, dirs, filenames in os.walk(path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fname in filenames:
                if fname.endswith((".kt", ".kts")):
                    fpath = os.path.join(root, fname)
                    rel = os.path.relpath(fpath, path)
                    if _should_ignore(rel, ignore_patterns):
                        continue
                    try:
                        with open(fpath, errors="replace") as f:
                            content = f.read()
                        result.append({"path": rel, "content": content})
                    except OSError:
                        pass
    return result


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
