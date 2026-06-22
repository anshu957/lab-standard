"""Experiment index & scaffolding.

    python -m {{PKG}}.index build        # regenerate experiments/runs.jsonl from manifests/metrics
    python -m {{PKG}}.index new <slug>   # scaffold experiments/exp-NNNN_<slug>/

`runs.jsonl` is machine-readable and regenerable, so it never drifts. `experiments/INDEX.md` is the
human/agent-facing table; `new` auto-adds a stub row, so you only fill in the hypothesis/result text.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

from .provenance import find_root

EXP_RE = re.compile(r"exp-(\d{4})_")


def _exp_dir(root: Path) -> Path:
    d = root / "experiments"
    d.mkdir(exist_ok=True)
    return d


def build(root: Path) -> None:
    records = []
    for d in sorted(_exp_dir(root).glob("exp-*")):
        if not d.is_dir():
            continue
        rec = {"run_id": d.name}
        if (d / "manifest.json").exists():
            m = json.loads((d / "manifest.json").read_text())
            rec["timestamp"] = m.get("timestamp_utc")
            rec["git_commit"] = (m.get("git") or {}).get("commit")
            rec["seed"] = m.get("seed")
        if (d / "metrics.json").exists():
            rec["metrics"] = json.loads((d / "metrics.json").read_text())
        records.append(rec)
    out = _exp_dir(root) / "runs.jsonl"
    out.write_text("".join(json.dumps(r) + "\n" for r in records))
    print(f"wrote {out} ({len(records)} runs)")
    for r in records:
        commit = (r.get("git_commit") or "-")[:8]
        print(f"  {r['run_id']:32s} {commit:8s} {r.get('metrics', '')}")


def _append_index_row(text: str, row: str) -> str:
    """Insert a markdown table row after the last existing table row."""
    lines = text.splitlines()
    rows = [i for i, ln in enumerate(lines) if ln.lstrip().startswith("|")]
    if rows:
        lines.insert(rows[-1] + 1, row)
    else:
        lines += ["", row]
    return "\n".join(lines) + "\n"


def register_in_index(root: Path, name: str) -> None:
    """Auto-add a stub row for `name` to experiments/INDEX.md (so you never have to ask)."""
    index = _exp_dir(root) / "INDEX.md"
    row = f"| {name} | {date.today().isoformat()} | _(fill in: hypothesis/goal)_ | `just run {name}` | — | planned |"
    if index.exists():
        if name not in index.read_text():
            index.write_text(_append_index_row(index.read_text(), row))
    else:
        index.write_text(
            "# Experiments index\n\n"
            "| ID | Date | Hypothesis / goal | Command | Result | Status |\n"
            "|----|------|-------------------|---------|--------|--------|\n" + row + "\n"
        )


def new(root: Path, slug: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")
    nums = [int(EXP_RE.match(d.name).group(1))
            for d in _exp_dir(root).glob("exp-*") if EXP_RE.match(d.name)]
    name = f"exp-{(max(nums) + 1) if nums else 1:04d}_{slug}"
    d = _exp_dir(root) / name
    if d.exists():
        sys.exit(f"{d} already exists")
    d.mkdir(parents=True)
    (d / "config.yaml").write_text(_CONFIG_STUB)
    (d / "run.py").write_text(_RUN_STUB.replace("__NAME__", name))
    (d / "README.md").write_text(_README_STUB.replace("__NAME__", name))
    register_in_index(root, name)
    print(f"created {d}  (+ auto-registered in experiments/INDEX.md)")
    print(f"Next: fill {name}/README.md (hypothesis) + edit config.yaml + run.py, then `just run {name}`.")
    return name


_CONFIG_STUB = """\
# Config for experiment __NAME__. The resolved values are recorded in manifest.json at run time.
seed: 0
# Add parameters below, e.g.:
# n_components: 10
# kappa: 1.0e4
"""

_RUN_STUB = '''\
"""Experiment __NAME__. Self-contained: writes ALL outputs into this folder only."""
import json
from pathlib import Path

from {{PKG}} import config, provenance, tracking  # reuse the library; don't reinvent

RUN_DIR = Path(__file__).resolve().parent


def main():
    args = config.parse_args()
    cfg = config.load_config(args.config)
    seed = config.set_seed(cfg["seed"])

    # --- your experiment here. Write outputs only under RUN_DIR (e.g. RUN_DIR/"figures"). ---
    metrics = {}

    (RUN_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2))
    provenance.write_manifest(RUN_DIR, config=cfg, seed=seed)
    with tracking.run("{{PKG}}", run_name=RUN_DIR.name, params=cfg):
        import mlflow
        for k, v in metrics.items():
            mlflow.log_metric(k, v)


if __name__ == "__main__":
    main()
'''

_README_STUB = """\
# __NAME__

- **Hypothesis:** <what you predict, and why>
- **Success criterion:** <result that would confirm it>
- **Pivot criterion:** <result that would make you abandon or branch>
- **Command:** `just run __NAME__`  (or `just submit __NAME__` on HPC)
- **Parent:** <exp-id this branched from, or "—">

## Outcome
<fill in after the run: what happened, links to figures/metrics, conclusion>
"""


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    root = find_root(Path.cwd())
    if argv and argv[0] == "new" and len(argv) > 1:
        new(root, argv[1])
    elif not argv or argv[0] == "build":
        build(root)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
