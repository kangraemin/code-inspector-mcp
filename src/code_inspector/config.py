from __future__ import annotations

import json
import os
from typing import Any

from pydantic import BaseModel


class InspectorConfig(BaseModel):
    enabled: bool = True
    weight: float = 1.0
    config: str | None = None
    disabled_rules: list[str] = []


class ReadabilityConfig(BaseModel):
    max_function_lines: int = 30
    max_nesting_depth: int = 4


class ReusabilityConfig(BaseModel):
    min_abstraction_score: float = 6.0


class ArchitectureConfig(BaseModel):
    patterns: list[str] = []
    readability: ReadabilityConfig = ReadabilityConfig()
    reusability: ReusabilityConfig = ReusabilityConfig()


class ComplexityMetricConfig(BaseModel):
    enabled: bool = True
    max_per_function: int = 15


class DuplicationMetricConfig(BaseModel):
    enabled: bool = True
    min_tokens: int = 100


class CoverageMetricConfig(BaseModel):
    enabled: bool = True
    min_percent: float = 80.0


class MetricsConfig(BaseModel):
    complexity: ComplexityMetricConfig = ComplexityMetricConfig()
    duplication: DuplicationMetricConfig = DuplicationMetricConfig()
    coverage: CoverageMetricConfig = CoverageMetricConfig()


class CodeInspectorConfig(BaseModel):
    threshold: float = 7.0
    inspectors: dict[str, InspectorConfig] = {
        "detekt": InspectorConfig(weight=0.4),
        "ktlint": InspectorConfig(weight=0.3),
        "android_lint": InspectorConfig(weight=0.3),
    }
    metrics: MetricsConfig = MetricsConfig()
    severity_weights: dict[str, float] = {
        "error": 0.3,
        "warning": 0.1,
        "info": 0.05,
    }
    ignore: list[str] = ["**/generated/**", "**/build/**"]
    architecture: ArchitectureConfig = ArchitectureConfig()


CONFIG_FILENAME = ".code-inspector.json"


def load_config(project_path: str) -> CodeInspectorConfig | None:
    config_path = os.path.join(project_path, CONFIG_FILENAME)
    if not os.path.isfile(config_path):
        return None
    with open(config_path) as f:
        data = json.load(f)
    return CodeInspectorConfig(**data)


def save_config(project_path: str, config: CodeInspectorConfig) -> str:
    config_path = os.path.join(project_path, CONFIG_FILENAME)
    with open(config_path, "w") as f:
        json.dump(config.model_dump(), f, indent=2, ensure_ascii=False)
    return config_path


def deep_merge(base: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    result = base.copy()
    for key, value in updates.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result
