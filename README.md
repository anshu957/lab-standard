# Lab Standard

A consistent, lightweight structure for exploratory scientific projects — readable by both me and
AI coding agents across many sessions. Full spec: **[STANDARD.md](STANDARD.md)**.

## Contents
- `STANDARD.md` — the canonical spec (read this).
- `template/` — the project skeleton. New projects copy this (via the `/new-project` skill).
- `global/` — the cross-project pieces installed into `~/.claude`:
  - `CLAUDE.snippet.md` — the constitution block added to `~/.claude/CLAUDE.md`.
  - `skills/new-project`, `skills/new-experiment` — the workflow skills.
  - `hooks/guard_paths.py` — the PreToolUse guardrail.
  - `settings.fragment.json` — registers the hook.
- `install.sh` — wires `global/` into `~/.claude` on a machine. Idempotent.

## Set up on a new machine (e.g. HPC)
`~/.claude/` is per-machine — it is **not** synced by your account. On each machine:
```bash
git clone <your-git-host>/lab-standard ~/.claude/lab-standard
bash ~/.claude/lab-standard/install.sh
```
Update later with `cd ~/.claude/lab-standard && git pull && bash install.sh`.

## Daily use
- New project: `/new-project`
- New experiment/run: `/new-experiment`  (or `just new-exp <slug>` inside a project)
- Rebuild the run index: `just index`

## To version & share
This dir is a git repo. Add your lab's remote and push so the HPC (and labmates) can clone it:
```bash
cd ~/.claude/lab-standard
git remote add origin <your-git-host>/lab-standard
git push -u origin main
```
