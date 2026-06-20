<!-- LAB-STANDARD:BEGIN (managed by ~/.claude/lab-standard/install.sh — edit the source there) -->
## Lab Standard for scientific projects

All my research projects follow the Lab Standard at ~/.claude/lab-standard/STANDARD.md.

On entering ANY project, BEFORE writing code:
1. Read its `AGENTS.md` (project map) and `experiments/INDEX.md` (what's been tried).
2. Grep `src/` for an existing utility before writing a new one. Reuse, don't regenerate.

Where things go:
- Reusable code → `src/<pkg>/` (importable, tested). Don't duplicate logic into scripts.
- A new run/experiment → `experiments/exp-NNNN_slug/` via the `/new-experiment` skill.
  ALL of its outputs (figures, metrics, logs, SLURM .err/.out) stay inside that folder.
- Exploration → `notebooks/`. A cross-cutting decision → an ADR in `docs/decisions/`.
- NEVER write scripts/outputs to the repo root. NEVER modify `data/raw/`.

New project? Use `/new-project` to scaffold from the template — don't invent a layout.
<!-- LAB-STANDARD:END -->
