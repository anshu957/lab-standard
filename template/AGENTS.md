# AGENTS.md — {{PROJECT}}

> Read this fully before doing anything. It is the map of this project.
> (CLAUDE.md just imports this file, so this is the single source of truth for every agent.)

## What this project is
{{ONE_PARAGRAPH: the scientific goal, the main pipeline, the key data. Fill this in.}}

## Start here — every session, before writing code
1. Read `experiments/INDEX.md` — what has already been tried and its outcome. **Do not re-run a completed experiment.**
2. Read the most recent ADRs in `docs/decisions/` — *why* the project is the way it is.
3. Before writing a utility, **grep `src/{{PKG}}/`** for an existing one. Reuse, don't regenerate.

## Setup & commands
- Environment: `conda activate {{ENV}}`  (defined in `environment.yml`)
- Install package (once): `pip install -e .`
- Run an experiment locally: `just run <exp-id>`
- Submit an experiment to SLURM: `just submit <exp-id>`
- Start a new experiment: use the `/new-experiment` skill (scaffolds the folder + manifest + index row)
- Rebuild the experiments index: `just index`
- Tests: `pytest -x`

## Directory contract — READ / WRITE / NEVER
- `data/raw/`        — **READ ONLY.** Original inputs. Never modify, overwrite, or delete. (A hook blocks this.)
- `data/processed/`  — Derived data. Regenerable; safe to overwrite.
- `src/{{PKG}}/`      — Reusable, importable, tested library code. **Add new utilities HERE**, not in scripts.
- `experiments/`     — One folder per run: `exp-NNNN_slug/`. **All new run code + ALL its outputs go inside its own folder** (figures, metrics, logs, SLURM .err/.out). Never scatter outputs elsewhere.
- `notebooks/`       — Exploration & narrative only. Naming: `<phase>.<n>-<initials>-<desc>.ipynb` (phase 0 explore, 1 clean, 2 viz, 3 model, 4 publish).
- `docs/decisions/`  — Architecture Decision Records (ADRs), numbered and immutable.
- **NEVER write scripts or outputs to the repo root.** (A hook blocks this.)

## What goes where (the rule that keeps this clean)
- Logic you might call twice  → a function in `src/{{PKG}}/`.
- A specific run/analysis      → `experiments/exp-NNNN_slug/run.py` that *imports* `src/{{PKG}}/` and writes only into its own folder.
- A quick look                 → a numbered notebook.
- A decision that shapes the project → a new ADR.

## Experiment provenance (automatic)
Every experiment folder is self-describing. `/new-experiment` and `src/{{PKG}}/provenance.py` write a `manifest.json` capturing: git commit (+ dirty diff), conda env, seed, input/output hashes, host, and SLURM job id. Metrics go to a local MLflow store (`mlruns/`) via `src/{{PKG}}/tracking.py`. When you finish a run, update its row in `experiments/INDEX.md`.

## Conventions
- No hardcoded params: every experiment reads a `config.yaml` (see `src/{{PKG}}/config.py`); the resolved config is saved into the run folder.
- Ask before: adding a dependency, changing `data/raw/`, or deleting anything in `experiments/`.
- Finished a run, or made a project-shaping choice? Leave a trace (INDEX.md row / new ADR) so the next session isn't blind.

<!-- Maintainer note (stripped from agent context, costs no tokens):
     Keep this file under ~200 lines. For each line ask "would removing it cause a mistake?" If not, cut it. -->
