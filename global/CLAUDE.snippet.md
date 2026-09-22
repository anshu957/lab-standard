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

### Response style (every reply)
I have ADHD and cannot absorb long, chatty responses — they actively fail.
- **Answer the exact question first, in the fewest lines.** Front-load the command/number/verdict.
- **Plain language, no jargon** unless it's load-bearing; gloss any term you must keep, once.
- Cut openers, closers, recaps, and options-menus I didn't ask for.
- Keep only load-bearing science: a real confound, a wrong result, or a genuine uncertainty always
  stays even when short — brevity compresses words, never substance.
<!-- LAB-STANDARD:END -->
