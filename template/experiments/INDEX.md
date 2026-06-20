# Experiments index — {{PROJECT}}

Append-only registry of every experiment. **The next session (human or agent) reads this first.**
Add a row when you START an experiment; fill in Result/Status when it finishes. Never delete a row —
mark it `superseded` instead. `just index` can regenerate the machine-readable `runs.jsonl` from each
run's `manifest.json` + `metrics.json`, so this table can never silently drift from ground truth.

Before running, write the experiment's hypothesis into its own `experiments/exp-NNNN_slug/README.md`
(Hypothesis / Success criterion / Pivot criterion / exact command). That stops post-hoc story-fitting.

| ID | Date | Hypothesis (one line) | Command / config | Result | Status |
|----|------|-----------------------|------------------|--------|--------|
| _example_ exp-0001_baseline | 2026-06-20 | Baseline pipeline reproduces published usage | `just run exp-0001_baseline` | — | template |

<!-- Statuses: planned | running | done | failed | superseded.
     Optional: add a "parent" note in the run's README to record which experiment it branched from. -->
