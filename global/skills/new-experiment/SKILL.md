---
name: new-experiment
description: Start a new experiment/run in a Lab-Standard scientific project. Use whenever beginning a new analysis, model run, parameter sweep, diagnostic, or any work that produces results. Scaffolds a self-contained experiments/exp-NNNN_slug/ folder (config + run.py + provenance manifest + MLflow + a hypothesis README) and registers it in experiments/INDEX.md, so the run is reproducible and the next session can find it.
---

# Start a new experiment

Goal: every new run lives in its own self-describing folder under `experiments/`, never scattered.
Reuse the project's existing tooling — do NOT hand-write manifest/provenance/index logic.

## Steps
1. **Confirm you're in a Lab-Standard project.** The project root has a `.labstd` marker and an
   `AGENTS.md`. If not, this skill doesn't apply — consider `/new-project` instead.

2. **Read context first** (this is the whole point of the standard): skim `experiments/INDEX.md`
   and recent `docs/decisions/`. If a completed experiment already answers the question, say so
   and stop instead of duplicating it.

3. **Pick a short slug** (kebab-case, e.g. `kappa-sweep`, `velocity-feature`). Scaffold the folder:
   ```bash
   just new-exp <slug>        # or: python -m <pkg>.index new <slug>
   ```
   This creates `experiments/exp-NNNN_<slug>/` with `config.yaml`, `run.py`, and `README.md`.

4. **Fill the hypothesis.** Edit `experiments/exp-NNNN_<slug>/README.md` *with the user*:
   Hypothesis, Success criterion, Pivot criterion, Parent experiment. Pre-registering this prevents
   post-hoc story-fitting. Ask the user if any field is unclear — don't invent the science.

5. **Write the experiment.** Put reusable logic in `src/<pkg>/` (check first whether it already
   exists — grep before writing). Keep `run.py` thin: it loads `config.yaml`, calls `src/`, and
   writes **all** outputs under the run folder (`figures/`, `metrics.json`, etc.). `run.py` already
   calls `provenance.write_manifest(...)` and `tracking.run(...)`; keep those.

6. **Register it.** Add one row to `experiments/INDEX.md` (ID, date, one-line hypothesis, command,
   `planned`). After the run finishes, update Result + Status and run `just index`.

## Rules
- All outputs stay inside the experiment folder — including SLURM `.err/.out` (use `just submit`).
- Never modify `data/raw/`. Never write to the repo root.
- Don't reinvent helpers that exist in `src/<pkg>/` (`config`, `provenance`, `tracking`, `index`).
