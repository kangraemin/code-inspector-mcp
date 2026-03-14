from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class Issue(BaseModel):
    file: str
    line: int
    column: int | None = None
    rule: str
    message: str
    severity: Literal["error", "warning", "info"]
    source: Literal["detekt", "ktlint", "android_lint"]


class ToolResult(BaseModel):
    tool: str
    score: float
    issues: list[Issue] = []
    available: bool = True
    error: str | None = None


class InspectionResult(BaseModel):
    path: str
    scope: str
    overall_score: float
    passed: bool
    threshold: float
    tool_results: list[ToolResult] = []
    summary: str
