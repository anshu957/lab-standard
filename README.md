# Lab Standard

A fixed structure and set of guardrails for exploratory scientific projects, so a project stays legible across many sessions — to me and to any coding agent. Spec: **[STANDARD.md](STANDARD.md)**.

## Layout
- `STANDARD.md` — the spec.
- `template/` — the project skeleton, copied by `/new-project`.
- `global/` — pieces installed into `~/.claude`:
  - `CLAUDE.snippet.md` — the block added to `~/.claude/CLAUDE.md`.
  - `skills/` — `new-project`, `new-experiment`.
  - `hooks/` — `guard_paths.py` (path guard), `ground_check.sh`, `session_state.sh`, `finish_gate.sh` (commit gate).
  - `settings.fragment.json` — wires the hooks into `settings.json`.
- `install.sh` — copies `global/` into `~/.claude`. Idempotent, makes backups.

## New machine
`~/.claude/` is per-machine and not synced by your account, so set it up on each one:
```bash
git clone git@github.com:anshu957/lab-standard.git ~/.claude/lab-standard
bash ~/.claude/lab-standard/install.sh   # restart open Claude Code sessions after
```
Update later: `cd ~/.claude/lab-standard && git pull && bash install.sh`.

## Daily use
- `/new-project` — scaffold a project.
- `/new-experiment` (or `just new-exp <slug>`) — start a run.
- `just check` — run the guardrails (also runs at commit time).
- `just index` — rebuild the run index.
