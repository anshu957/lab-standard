"""MLflow tracking — local file store, zero infrastructure.

Runs are logged to `<project_root>/mlruns/` (no server, no account; view later with `mlflow ui`).
Each run is auto-tagged with the git commit so metrics trace back to code.

Usage inside an experiment's run.py:
    from {{PKG}} import tracking
    with tracking.run("{{PKG}}", run_name="exp-0001_baseline", params=cfg):
        import mlflow
        mlflow.log_metric("heldout_ll", ll)
        mlflow.log_artifact("figures/usage.png")
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

from .provenance import _git_info, find_root


def _flatten(d: dict, prefix: str = "") -> dict:
    out = {}
    for k, v in (d or {}).items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(_flatten(v, key + "."))
        else:
            out[key] = v
    return out


@contextmanager
def run(experiment: str, run_name: str, params: dict | None = None, project_root=None):
    """Open an MLflow run against the project-local store. Yields the active run."""
    import mlflow

    root = Path(project_root) if project_root else find_root(Path.cwd())
    mlflow.set_tracking_uri((root / "mlruns").as_uri())
    mlflow.set_experiment(experiment)
    with mlflow.start_run(run_name=run_name) as active:
        git = _git_info(root)
        if git.get("commit"):
            mlflow.set_tag("git_commit", git["commit"])
            mlflow.set_tag("git_dirty", str(git.get("dirty")))
        if params:
            mlflow.log_params(_flatten(params))
        yield active
