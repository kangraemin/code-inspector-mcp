from __future__ import annotations

import hashlib
from collections import defaultdict


def analyze_duplication(
    files: list[dict], window_size: int = 5
) -> dict:
    """Detect duplicate code blocks across files.

    Args:
        files: List of {"path": str, "content": str}
        window_size: Number of lines per sliding window block
    """
    block_map: dict[str, list[dict]] = defaultdict(list)
    total_lines = 0

    for file_info in files:
        content = file_info.get("content")
        if not content:
            continue

        lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip() and not line.strip().startswith("//") and not line.strip().startswith("/*")
        ]
        total_lines += len(lines)

        if len(lines) < window_size:
            continue

        for i in range(len(lines) - window_size + 1):
            block = "\n".join(lines[i : i + window_size])
            block_hash = hashlib.md5(block.encode()).hexdigest()
            block_map[block_hash].append({
                "file": file_info["path"],
                "start_line": i + 1,
                "block": block,
            })

    duplicates: list[dict] = []
    duplicated_lines = 0
    seen_blocks: set[str] = set()

    for block_hash, locations in block_map.items():
        if len(locations) > 1 and block_hash not in seen_blocks:
            seen_blocks.add(block_hash)
            duplicates.append({
                "block_hash": block_hash,
                "locations": [
                    {"file": loc["file"], "start_line": loc["start_line"]}
                    for loc in locations
                ],
                "lines": window_size,
                "sample": locations[0]["block"],
            })
            duplicated_lines += window_size * len(locations)

    duplication_pct = round(
        (duplicated_lines / total_lines * 100) if total_lines > 0 else 0, 2
    )

    return {
        "duplicates": duplicates,
        "total_lines": total_lines,
        "duplicated_lines": duplicated_lines,
        "duplication_percentage": duplication_pct,
    }
