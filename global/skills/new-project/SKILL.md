---
name: new-project
description: Scaffold a new scientific project from the Lab Standard template. Use when starting a brand-new research project, repo, or analysis codebase from scratch. Creates the standard structure (src/ package, experiments/, notebooks/, data/, docs/decisions/, AGENTS.md, justfile, environment.yml, MLflow + provenance helpers) so every future session has a consistent map to ground to.
---

# Scaffold a new Lab-Standard project

Template lives at `~/.claude/lab-standard/template/`. The canonical spec is
`~/.claude/lab-standard/STANDARD.md` — read it if unsure why a convention exists.

## Step 1 — gather parameters (ask the user; don't assume)
- **Target directory** (absolute path for the new project)
- **Project title** (human-readable, e.g. "Gait KPMS mutants")
- **Package name** (`<pkg>`: a valid Python identifier, lowercase, no spaces, e.g. `gaitkpms`)
- **Conda env name** (`<env>`, e.g. `gaitkpms`)
- **Where the real data lives** (absolute path on shared store / HPC scratch)

## Step 2 — confirm, then copy the template
Per the user's standing rule, **show this and get explicit go-ahead before copying** (`cp`):
```bash
cp -r ~/.claude/lab-standard/template <TARGET_DIR>
mv  <TARGET_DIR>/src/PKG <TARGET_DIR>/src/<pkg>
```

## Step 3 — substitute placeholders
Replace the three tokens everywhere, and the package name in pyproject:
```bash
cd <TARGET_DIR>
grep -rlZ -e '{{PROJECT}}' -e '{{PKG}}' -e '{{ENV}}' . | xargs -0 sed -i \
    -e 's/{{PROJECT}}/<Project Title>/g' \
    -e 's/{{PKG}}/<pkg>/g' \
    -e 's/{{ENV}}/<env>/g'
sed -i 's/^name = "PKG"/name = "<pkg>"/' pyproject.toml
```
Then fill the remaining human placeholders by editing the files directly (don't sed these — they
need real prose): `{{ONE_PARAGRAPH}}` and `{{DATA_LOCATION}}` in `AGENTS.md` and `README.md`.
Note: the `justfile` keeps `{{exp}}`/`{{slug}}` — those are `just`'s own args, leave them.

## Step 4 — initialize
```bash
cd <TARGET_DIR>
git init && git add -A && git commit -m "Scaffold from Lab Standard"
# environment (ask before running — this can be slow / large):
# mamba env create -f environment.yml && conda activate <env> && pip install -e .
```

## Step 5 — orient the user
Tell them: edit `AGENTS.md`'s "What this project is", point `data/raw/` at the real data, then use
`/new-experiment` for the first run. Confirm the `.labstd` marker is present (it activates the
path-guard hook for this project).
