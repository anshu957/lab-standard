"""Consistency checks — keep the repo's structure honest (Lab Standard).

Run: `just check`  or  `python -m {{PKG}}.check`. Asserts structural invariants so docs/structure
can't silently drift:
  1. every experiments/exp-*/ has a README.md
  2. every experiments/exp-*/ is listed in experiments/INDEX.md  (no undocumented runs)
  3. no dangling symlinks under data/
  4. no stray files at the repo root (only the declared Lab-Standard files)
Exit 0 = all pass; 1 = a failure. Stdlib-only, self-contained, so it runs anywhere (pre-commit/CI).
Add project-specific assertions as new check_* functions registered in CHECKS.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ALLOWED_ROOT = {
    "README.md", "AGENTS.md", "CLAUDE.md", "CLAUDE.local.md", "pyproject.toml",
    "justfile", "Justfile", "environment.yml", "requirements.txt", ".gitignore",
    ".labstd", ".python-version", "LICENSE", "setup.cfg", "Makefile", "uv.lock",
    ".pre-commit-config.yaml",
}


def find_root(start: Path) -> Path:
    for d in (start, *start.parents):
        if (d / ".labstd").exists():
            return d
    return start


def check_experiment_readmes(root: Path) -> list:
    return [f"experiment {d.name} has no README.md"
            for d in sorted((root / "experiments").glob("exp-*"))
            if d.is_dir() and not (d / "README.md").exists()]


def check_index_sync(root: Path) -> list:
    index = root / "experiments" / "INDEX.md"
    listed = set(re.findall(r"exp-\d{4}_[A-Za-z0-9._-]+", index.read_text())) if index.exists() else set()
    return [f"experiment {d.name} is not listed in experiments/INDEX.md"
            for d in sorted((root / "experiments").glob("exp-*"))
            if d.is_dir() and d.name not in listed]


def check_dangling_symlinks(root: Path) -> list:
    data = root / "data"
    if not data.exists():
        return []
    return [f"dangling symlink: {p.relative_to(root)} -> {p.readlink()}"
            for p in data.rglob("*") if p.is_symlink() and not p.exists()]


def check_root_clean(root: Path) -> list:
    return [f"stray file at repo root: {p.name}"
            for p in root.iterdir() if p.is_file() and p.name not in ALLOWED_ROOT]


CHECKS = {
    "experiment READMEs": check_experiment_readmes,
    "INDEX.md sync": check_index_sync,
    "no dangling data symlinks": check_dangling_symlinks,
    "clean repo root": check_root_clean,
}


def main() -> int:
    root = find_root(Path.cwd())
    failures = 0
    for name, fn in CHECKS.items():
        errs = fn(root)
        if errs:
            failures += len(errs)
            print(f"x {name}:")
            for e in errs:
                print(f"    - {e}")
        else:
            print(f"ok {name}")
    if failures:
        print(f"\n{failures} consistency problem(s) -- fix before committing.")
        return 1
    print("\nAll consistency checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
