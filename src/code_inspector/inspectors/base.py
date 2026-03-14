from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
from abc import ABC, abstractmethod

from code_inspector.models import ToolResult


class BaseInspector(ABC):
    name: str = ""

    @abstractmethod
    async def run(self, path: str, files: list[str] | None = None, severity_weights: dict[str, float] | None = None) -> ToolResult:
        ...

    def is_available(self) -> bool:
        return shutil.which(self.name) is not None

    async def _run_subprocess(
        self, cmd: list[str], cwd: str, timeout: int = 120
    ) -> tuple[str, str, int]:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            return "", "timeout", -1
        return (
            stdout.decode(errors="replace"),
            stderr.decode(errors="replace"),
            proc.returncode or 0,
        )

    def _count_kt_files(self, path: str) -> int:
        count = 0
        for root, _, filenames in os.walk(path):
            for f in filenames:
                if f.endswith((".kt", ".kts")):
                    count += 1
        return max(count, 1)

    def _get_changed_files(self, path: str, extensions: list[str]) -> list[str]:
        ext_args = [f"-- *{ext}" for ext in extensions]
        cmd = ["git", "diff", "--name-only", "--diff-filter=ACMR", "HEAD"] + ext_args
        try:
            result = subprocess.run(
                cmd, cwd=path, capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                return []
            return [f for f in result.stdout.strip().splitlines() if f]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []
