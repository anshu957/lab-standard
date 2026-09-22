#!/usr/bin/env python3
"""Lab-Standard PreToolUse guard.

Hard-blocks three things, but ONLY inside a Lab-Standard project (a dir tree containing a `.labstd`
marker) so it never interferes with other repos:
  1. Any write/edit to `data/raw/`  (raw data is immutable).
  2. Creating a NEW file directly in the repo root  (scripts/outputs belong in experiments/ or src/).
  3. Creating a NEW file inside an UNDECLARED top-level directory  (every substantial artifact must
     live in a declared home: experiments/ for runs, deliverables/<slug>/ for derived artifacts like
     talks/manuscripts, src/ for reusable code, notebooks/ for exploration). This is what stops a
     stray `talk/` or `analysis_v2/` from silently appearing at the top level.

Editing files that already exist (anywhere) is allowed. NOTE: this only sees the Write/Edit family;
files created via Bash (e.g. a .pptx built by a skill) bypass it — `check.py`'s clean-root check is
the commit-time backstop for those.
Contract: exit 0 = allow; exit 2 + stderr = block (reason shown to Claude). Fails OPEN on any error.
"""
import json
import sys
from pathlib import Path

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
ALLOWED_ROOT = {
    "README.md", "AGENTS.md", "CLAUDE.md", "CLAUDE.local.md", "CONCLUSIONS.md", "WORKLOG.md",
    "pyproject.toml", "justfile", "Justfile", "environment.yml", "requirements.txt",
    ".gitignore", ".labstd", ".python-version", "LICENSE", "setup.cfg", "Makefile",
    "uv.lock", ".pre-commit-config.yaml",
}
# The only directories allowed directly under the repo root. Everything substantial lives in one of
# these; a new top-level dir means an undeclared, unregistered artifact — block it.
ALLOWED_ROOT_DIRS = {
    "src", "data", "experiments", "deliverables", "notebooks", "docs", "tests", "slurm",
    "mlruns", ".git", ".github", ".ipynb_checkpoints", ".pytest_cache", "__pycache__",
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

    # 3) no NEW files inside an undeclared top-level directory
    try:
        rel = target.relative_to(root)
    except ValueError:
        sys.exit(0)  # outside the project — not our business
    if len(rel.parts) >= 2 and not target.exists():
        top = rel.parts[0]
        if top not in ALLOWED_ROOT_DIRS:
            sys.stderr.write(
                f"[Lab Standard] Blocked: '{top}/' is not a declared top-level directory, so "
                f"'{rel}' has no registered home. A run -> experiments/<exp-id>/ (use /new-experiment); "
                f"a derived artifact (talk, manuscript, report) -> deliverables/<slug>/ with a README "
                f"naming the experiments it draws on. Add the dir to ALLOWED_ROOT_DIRS + AGENTS.md only "
                f"if it's a deliberate new part of the project's structure."
            )
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)  # never block legitimate work because of a guard bug
