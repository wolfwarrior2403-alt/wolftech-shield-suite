"""Reads the rule-book markdown tables so tests can compare them with the code."""
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"


def parse(filename: str, prefix: str) -> dict[str, dict]:
    rows = {}
    for line in (DOCS / filename).read_text(encoding="utf-8").splitlines():
        if not line.startswith(f"| {prefix}"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows[cells[0]] = {"cells": cells, "status": cells[-2], "scored": cells[-1], "line": line}
    return rows


def scored_ids(filename: str, prefix: str) -> set[str]:
    return {rid for rid, row in parse(filename, prefix).items() if row["scored"].startswith("Yes")}
