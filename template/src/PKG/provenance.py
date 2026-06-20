"""Provenance: write a self-describing manifest.json into a run folder.

Captures git commit (+ uncommitted diff), conda/pip environment lock, seed, host, SLURM job info,
and sha256 of input/output files. This is what makes a run reproducible without external context.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_MARKERS = (".labstd", ".git", "pyproject.toml")


def _run(cmd) -> str | None:
    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return None


def find_root(start: str | Path) -> Path:
    """Walk up from `start` to the project root (first dir with a Lab-Standard marker)."""
    p = Path(start).resolve()
    for d in (p, *p.parents):
        if any((d / m).exists() for m in _MARKERS):
            return d
    return p


def sha256(path: str | Path, block: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(block), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_info(root: Path, run_dir: Path | None = None) -> dict:
    commit = _run(["git", "-C", str(root), "rev-parse", "HEAD"])
    if not commit:
        return {"commit": None, "note": "not a git repo"}
    info = {
        "commit": commit,
        "branch": _run(["git", "-C", str(root), "rev-parse", "--abbrev-ref", "HEAD"]),
        "dirty": bool(_run(["git", "-C", str(root), "status", "--porcelain"])),
    }
    # A commit recorded without flagging a dirty tree is misleading — save the diff.
    if info["dirty"] and run_dir is not None:
        diff = _run(["git", "-C", str(root), "diff", "HEAD"])
        if diff:
            (run_dir / "git_diff.patch").write_text(diff)
            info["diff_file"] = "git_diff.patch"
    return info


def _env_lock(run_dir: Path) -> str | None:
    txt = _run(["conda", "env", "export", "--no-builds"])
    if txt:
        (run_dir / "environment.lock.yml").write_text(txt)
        return "environment.lock.yml"
    txt = _run([sys.executable, "-m", "pip", "freeze"])
    if txt:
        (run_dir / "pip-freeze.txt").write_text(txt)
        return "pip-freeze.txt"
    return None


def write_manifest(run_dir, config=None, seed=None, inputs=None, outputs=None,
                   project_root=None) -> dict:
    """Write `<run_dir>/manifest.json` and return the manifest dict."""
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    root = Path(project_root) if project_root else find_root(run_dir)
    slurm = {k: os.environ[k] for k in
             ("SLURM_JOB_ID", "SLURMD_NODENAME", "SLURM_JOB_PARTITION") if k in os.environ}
    manifest = {
        "run_id": run_dir.name,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "command": " ".join([Path(sys.executable).name, *sys.argv]),
        "git": _git_info(root, run_dir),
        "host": {"hostname": platform.node(), "platform": platform.platform(),
                 "python": platform.python_version()},
        "slurm": slurm or None,
        "env_lock": _env_lock(run_dir),
        "seed": seed,
        "inputs": [{"path": str(p), "sha256": sha256(p)}
                   for p in (inputs or []) if Path(p).is_file()],
        "outputs": [{"path": str(p), "sha256": sha256(p)}
                    for p in (outputs or []) if Path(p).is_file()],
        "config": config,
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest
