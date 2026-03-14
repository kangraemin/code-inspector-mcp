from __future__ import annotations

import re

BRANCH_KEYWORDS = re.compile(
    r"\b(if|else\s+if|when|for|while|do|catch|&&|\|\|)\b"
)

FUNCTION_PATTERN = re.compile(
    r"^\s*(?:(?:private|public|protected|internal|override|suspend|inline)\s+)*fun\s+(\w+)"
)


def analyze_complexity(
    content: str, file_path: str, max_per_function: int = 15
) -> dict:
    lines = content.splitlines()
    functions: list[dict] = []
    current_func: str | None = None
    current_start: int = 0
    brace_depth = 0
    branch_count = 0
    func_lines = 0

    for i, line in enumerate(lines, 1):
        match = FUNCTION_PATTERN.match(line)
        if match and brace_depth == 0:
            if current_func:
                functions.append({
                    "name": current_func,
                    "line": current_start,
                    "complexity": branch_count + 1,
                    "lines": func_lines,
                })
            current_func = match.group(1)
            current_start = i
            branch_count = 0
            func_lines = 0
            brace_depth = 0

        if current_func:
            func_lines += 1
            brace_depth += line.count("{") - line.count("}")
            branch_count += len(BRANCH_KEYWORDS.findall(line))

            if brace_depth <= 0 and func_lines > 1:
                functions.append({
                    "name": current_func,
                    "line": current_start,
                    "complexity": branch_count + 1,
                    "lines": func_lines,
                })
                current_func = None
                brace_depth = 0

    if current_func:
        functions.append({
            "name": current_func,
            "line": current_start,
            "complexity": branch_count + 1,
            "lines": func_lines,
        })

    violations = [f for f in functions if f["complexity"] > max_per_function]
    avg = sum(f["complexity"] for f in functions) / len(functions) if functions else 0

    return {
        "file": file_path,
        "functions": functions,
        "violations": violations,
        "average_complexity": round(avg, 2),
        "max_complexity": max(
            (f["complexity"] for f in functions), default=0
        ),
    }
