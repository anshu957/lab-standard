# 0001. Adopt the Lab Standard project structure

## Status
accepted

## Context
Exploratory scientific projects accumulate scattered scripts, results, and logs because each work
session (especially each AI-agent session) starts fresh with no shared map, and improvises its own
layout. The result becomes unreadable and unreproducible.

## Decision
This project follows the Lab Standard (`~/.claude/lab-standard/STANDARD.md`):
- Reusable code in `src/`, one self-contained folder per run under `experiments/`, exploration in
  `notebooks/`, decisions recorded as ADRs here in `docs/decisions/`.
- `data/raw/` is immutable; nothing is written to the repo root.
- Each run is self-describing (manifest with git commit + env + seed; metrics in MLflow).
- `AGENTS.md` is the always-read map; a global rule + a path-guard hook keep every session consistent.

## Consequences
- Easier: a fresh session (or future-you) can reconstruct project state from INDEX.md + ADRs; results
  are traceable to the code/config/commit that produced them.
- Harder / costs: a little upfront ceremony per experiment (a folder + manifest + an index row). This
  is automated by the `/new-experiment` skill, so the cost is small.
- ADRs are immutable: to change a decision, add a new ADR that supersedes this one.
