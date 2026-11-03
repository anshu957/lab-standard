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
- **RAM-monitor every job (hook-enforced).** Run python/R/`just run` as `bash ~/.claude/hooks/memwatch.sh <cmd>` (kills at `MEMWATCH_CAP_GB`, default 70% of RAM, or system free < 1 GB). Write memory-light code (no full AnnData copies; `del` + `gc` per loop). Report the `peak_rss` line.

New project? Use `/new-project` to scaffold from the template — don't invent a layout.

### Grounding & consistency (every session, every task)
Long sessions drift — the newest result crowds out earlier ones and you start asserting their opposite.
Guard against it:
- Each project keeps a root **`CONCLUSIONS.md`** ledger: `## Established` (verified, + evidence pointer),
  `## Open`, `## Retracted` (disproved, + why — so they don't come back). The `UserPromptSubmit` hook
  injects it into every prompt; it also sits at the repo root.
- **Before any analytical claim, recommendation, or task: reconcile with `CONCLUSIONS.md`.**
- **Never contradict an `Established` entry without flagging the contradiction and re-deriving from
  evidence.** If evidence overturns it, move it to `Retracted` (with the reason) the same turn.
- **State established facts before new interpretation; mark new interpretation as tentative.**
- Reached or overturned a conclusion? **Update `CONCLUSIONS.md` the same turn.**

### Task lifecycle (every task, every session — enforced by hooks)
1. **START — read the state.** A `SessionStart` hook injects recent `git log`/`git status`, the
   `WORKLOG.md` tail, and `CONCLUSIONS.md`. Before acting, check it: **is this (or part of it) already
   done?** Don't redo finished work; reuse existing outputs.
2. **DURING — know what you're doing.** State the task and reconcile it with that state.
3. **FINISH — record what you did.** Append a dated entry to **`WORKLOG.md`** (what / why / result /
   what's next). A `Stop` hook **blocks finishing** if you changed real files (scripts/data/figures)
   without logging. Git is the never-stale ground truth — the log points to it; keep both current.

### Figures (every plot, every project)
- **Before writing ANY plotting code, invoke the `figure-hygiene` skill** and follow it (one figure = one question = one panel, the question as its bold title, no numbers/method notes on the plot → `figure_captions.md`). Ask me only when the design is genuinely ambiguous; run its `qa.py` and look at the PNG before showing.
- Save figures as **PDF only** (vector, publication-grade). Never emit the same figure in a second format (no parallel `.png`).
- Use **stable, descriptive filenames** so re-running a script **overwrites** the same file. Never spawn per-iteration variants (`_v2`, `_pt_ot`, timestamped copies) for the same plot.
- When you change or supersede a figure, **delete the old/stale file(s)** in the same step, so the `figures/` folder never accumulates duplicates or confusing leftovers.
- Title/caption each figure with **what method produced it** when the method isn't obvious (e.g. "Slingshot" vs a custom curve), so figures are never ambiguous.
- Skill source: github.com/anshu957/my-scientific-research-skills (`skills/figure-hygiene`).

### Thinking and reply style (every reply)
- Comes from `~/.claude/lab-standard/global/RULES.md` (3 core rules + 4 labels: Measured / Failed /
  Reasoning / Hunch), injected into every prompt by the `core_rules.sh` hook. Edit the rules there, not here.
<!-- LAB-STANDARD:END -->
