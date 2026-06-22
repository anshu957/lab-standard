#!/usr/bin/env python3
"""Lab-Standard PreToolUse guard.

Hard-blocks two things, but ONLY inside a Lab-Standard project (a dir tree containing a `.labstd`
marker) so it never interferes with other repos:
  1. Any write/edit to `data/raw/`  (raw data is immutable).
  2. Creating a NEW file directly in the repo root  (scripts/outputs belong in experiments/ or src/).

Editing files that already exist at the root (README, AGENTS.md, pyproject.toml, ...) is allowed.
Contract: exit 0 = allow; exit 2 + stderr = block (reason shown to Claude). Fails OPEN on any error.
"""
import json
import sys
from pathlib import Path

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
ALLOWED_ROOT = {
    "README.md", "AGENTS.md", "CLAUDE.md", "CLAUDE.local.md", "pyproject.toml",
    "justfile", "Justfile", "environment.yml", "requirements.txt", ".gitignore",
    ".labstd", ".python-version", "LICENSE", "setup.cfg", "Makefile", "uv.lock",
    ".pre-commit-config.yaml",
}


def find_root(start: Path):
    for d in (start, *start.parents):
        if (d / ".labstd").exists():
            return d
    return None


def main():
    raw = sys.stdin.read()
    data = json.loads(raw) if raw.strip() else {}
    if data.get("tool_name") not in WRITE_TOOLS:
        sys.exit(0)

    ti = data.get("tool_input", {}) or {}
    path_str = ti.get("file_path") or ti.get("notebook_path") or ti.get("path")
    if not path_str:
        sys.exit(0)

    target = Path(path_str)
    if not target.is_absolute():
        target = Path(data.get("cwd", ".")) / target
    target = target.resolve()

    root = find_root(target.parent)
    if root is None:
        sys.exit(0)  # not a Lab-Standard project — don't interfere

    # 1) data/raw is immutable
    raw_dir = (root / "data" / "raw").resolve()
    if raw_dir == target or raw_dir in target.parents:
        sys.stderr.write(
            f"[Lab Standard] Blocked: '{target}' is under data/raw/, which is READ-ONLY. "
            f"Write derived data to data/processed/ or into your experiment folder instead."
        )
        sys.exit(2)

    # 2) no NEW files at the repo root
    if target.parent == root and not target.exists() and target.name not in ALLOWED_ROOT:
        sys.stderr.write(
            f"[Lab Standard] Blocked: don't create new files in the project root ('{target.name}'). "
            f"Put run code/outputs in experiments/<exp-id>/ (use /new-experiment), reusable code in "
            f"src/, exploration in notebooks/. See AGENTS.md."
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)  # never block legitimate work because of a guard bug
