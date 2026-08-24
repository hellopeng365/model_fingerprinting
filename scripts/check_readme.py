#!/usr/bin/env python3
"""Lightweight structural checks for the survey README."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
PAPERS = ROOT / "resources" / "papers.md"

REQUIRED_HEADINGS = [
    "# 模型指纹技术研究进展",
    "## 1. 摘要",
    "## 2. 术语与边界",
    "## 3. 技术谱系",
    "## 4. 方法对照（精选）",
    "## 5. 2024–2026 研究进展概览",
    "## 10. 代表性论文与资源",
    "## 11. 本周更新要点（2026-08-24）",
]

REQUIRED_KEYWORDS = [
    "LLMPrint",
    "DuFFin",
    "FPEdit",
    "MergePrint",
    "LEAFBENCH",
    "HuRef",
    "Chain & Hash",
]


def check_trailing_whitespace(text: str, path: Path) -> list[str]:
    errors = []
    for i, line in enumerate(text.splitlines(), 1):
        if line.rstrip("\n").endswith(" ") or line.endswith("\t"):
            errors.append(f"{path}: line {i} has trailing whitespace")
    return errors


def check_tables(text: str, path: Path) -> list[str]:
    errors = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if "|" in lines[i] and i + 1 < len(lines) and re.match(r"^\|?\s*-+", lines[i + 1]):
            header_cols = [c for c in lines[i].strip().strip("|").split("|")]
            expected = len(header_cols)
            j = i + 1
            while j < len(lines) and "|" in lines[j]:
                cols = [c for c in lines[j].strip().strip("|").split("|")]
                if len(cols) != expected:
                    errors.append(
                        f"{path}: table column mismatch near line {j + 1}: "
                        f"expected {expected}, got {len(cols)}"
                    )
                j += 1
            i = j
        else:
            i += 1
    return errors


def main() -> int:
    errors: list[str] = []

    if not README.exists():
        print("README.md missing", file=sys.stderr)
        return 1
    if not PAPERS.exists():
        print("resources/papers.md missing", file=sys.stderr)
        return 1

    readme = README.read_text(encoding="utf-8")
    papers = PAPERS.read_text(encoding="utf-8")

    if not readme.endswith("\n"):
        errors.append("README.md must end with a newline")
    if not papers.endswith("\n"):
        errors.append("resources/papers.md must end with a newline")

    for heading in REQUIRED_HEADINGS:
        if heading not in readme:
            errors.append(f"missing heading: {heading}")

    for keyword in REQUIRED_KEYWORDS:
        if keyword not in readme:
            errors.append(f"missing keyword in README: {keyword}")

    if "更新时间：2026-08-24" not in readme:
        errors.append("README update date is not 2026-08-24")

    errors.extend(check_trailing_whitespace(readme, README))
    errors.extend(check_trailing_whitespace(papers, PAPERS))
    errors.extend(check_tables(readme, README))
    errors.extend(check_tables(papers, PAPERS))

    if errors:
        print("CHECK FAILED:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("CHECK PASSED: README and resources/papers.md look consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
