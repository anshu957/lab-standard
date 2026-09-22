"""Consistency checks — keep the repo's structure honest (Lab Standard).

Run: `just check`  or  `python -m {{PKG}}.check`. Asserts structural invariants so docs/structure
can't silently drift:
  1. every experiments/exp-*/ has a README.md
  2. every experiments/exp-*/ is listed in experiments/INDEX.md  (no undocumented runs)
  3. no dangling symlinks under data/
  4. no stray files at the repo root (only the declared Lab-Standard files)
  5. no undeclared top-level directories (every artifact has a registered home)
  6. every deliverables/<slug>/ has a README.md (derived artifacts are registered too)
  7. no logic duplication: nothing under experiments/ redefines a def/class that lives in src/
Exit 0 = all pass; 1 = a failure. Stdlib-only, self-contained, so it runs anywhere (pre-commit/CI).
This runs via .pre-commit-config on every `git commit`, so the checks can't be forgotten.
Add project-specific assertions as new check_* functions registered in CHECKS.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ALLOWED_ROOT = {
    "README.md", "AGENTS.md", "CLAUDE.md", "CLAUDE.local.md", "CONCLUSIONS.md", "WORKLOG.md",
    "pyproject.toml", "justfile", "Justfile", "environment.yml", "requirements.txt", ".gitignore",
    ".labstd", ".python-version", "LICENSE", "setup.cfg", "Makefile", "uv.lock",
    ".pre-commit-config.yaml", ".DS_Store",
}
# Keep in sync with ALLOWED_ROOT_DIRS in ~/.claude/hooks/guard_paths.py.
ALLOWED_ROOT_DIRS = {
    "src", "data", "experiments", "deliverables", "notebooks", "docs", "tests", "slurm",
    "mlruns", ".git", ".github", ".ipynb_checkpoints", ".pytest_cache", "__pycache__",
}
# Names that legitimately recur in run scripts and are NOT a duplication smell.
DUP_IGNORE = {"main", "run", "setup", "parse_args"}


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


def check_root_dirs_declared(root: Path) -> list:
    """No undeclared top-level directory — the backstop that catches a stray `talk/` even when it
    was created via Bash (which the PreToolUse guard can't see)."""
    return [f"undeclared top-level directory: {p.name}/  "
            f"(a run -> experiments/; a derived artifact -> deliverables/<slug>/; "
            f"or add it to ALLOWED_ROOT_DIRS + AGENTS.md if it's a deliberate new part of the layout)"
            for p in root.iterdir() if p.is_dir() and p.name not in ALLOWED_ROOT_DIRS]


def check_deliverable_readmes(root: Path) -> list:
    """Derived artifacts (talks, manuscripts, reports) are registered too: each needs a README
    stating its purpose and which experiments it draws on."""
    deliv = root / "deliverables"
    if not deliv.exists():
        return []
    return [f"deliverable {d.name} has no README.md (state its purpose + source experiments)"
            for d in sorted(deliv.iterdir())
            if d.is_dir() and not (d / "README.md").exists()]


def _defs(py: Path):
    """Yield (name, body_hash, n_statements) for each top-level func/class in a .py file.

    The hash is over the AST-normalized BODY with the docstring stripped — so it detects real
    copy-paste (identical implementation) and is blind to names, comments, and formatting. This is
    deliberately NOT name-based: two different functions that happen to share a generic name (e.g.
    `_figure`, `panel_drift`) are NOT flagged; only functions whose actual code matches are."""
    try:
        tree = ast.parse(py.read_text(), filename=str(py))
    except (SyntaxError, UnicodeDecodeError):
        return
    for n in tree.body:
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        body = list(n.body)
        if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant):
            body = body[1:]  # drop docstring
        yield n.name, hash(ast.dump(ast.Module(body=body, type_ignores=[]))), len(body)


# A body with fewer statements than this is too trivial to be a meaningful duplicate (e.g. a one-line
# wrapper), so matches on it are ignored to avoid noise.
DUP_MIN_STATEMENTS = 3


def check_no_duplicated_logic(root: Path) -> list:
    """The DRY rail (paradigm-agnostic): the SAME implementation must not live in two places, so it
    can't silently drift into two different versions. Flags, by comparing normalized function BODIES:
      (a) a func/class under experiments/ whose body is identical to one in src/ (import it instead), and
      (b) a body that is copy-pasted across two or more experiment files (promote it to src/).
    Different code that merely shares a name is NOT flagged."""
    experiments = root / "experiments"
    if not experiments.exists():
        return []
    errs = []

    src_bodies: dict = {}  # body_hash -> "pkg/mod.py::name"
    src = root / "src"
    if src.exists():
        for py in src.rglob("*.py"):
            for name, h, ns in _defs(py):
                if name not in DUP_IGNORE and ns >= DUP_MIN_STATEMENTS:
                    src_bodies.setdefault(h, f"{py.relative_to(root)}::{name}")

    exp_bodies: dict = {}  # body_hash -> [ "exp/..py::name", ... ]
    for py in experiments.rglob("*.py"):
        for name, h, ns in _defs(py):
            if name in DUP_IGNORE or ns < DUP_MIN_STATEMENTS:
                continue
            if h in src_bodies:
                errs.append(f"{py.relative_to(root)}::{name} is a copy of {src_bodies[h]} — "
                            f"import it from src/, don't re-implement it")
            exp_bodies.setdefault(h, []).append(f"{py.relative_to(root)}::{name}")

    for h, locs in sorted(exp_bodies.items(), key=lambda kv: kv[1]):
        if len(locs) > 1:
            errs.append(f"identical code copy-pasted across experiments ({', '.join(sorted(locs))}) — "
                        f"promote it to src/ and import it")
    return errs


CHECKS = {
    "experiment READMEs": check_experiment_readmes,
    "INDEX.md sync": check_index_sync,
    "no dangling data symlinks": check_dangling_symlinks,
    "clean repo root": check_root_clean,
    "declared top-level dirs": check_root_dirs_declared,
    "deliverable READMEs": check_deliverable_readmes,
    "no duplicated src logic": check_no_duplicated_logic,
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
