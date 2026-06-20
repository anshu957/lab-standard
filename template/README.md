# {{PROJECT}}

{{ONE_PARAGRAPH: what this project is and what question it answers.}}

## Quickstart
```bash
conda env create -f environment.yml   # or: mamba env create -f environment.yml
conda activate {{ENV}}
pip install -e .                       # editable install of src/{{PKG}}
just                                   # list tasks
```

## Layout
This project follows the **Lab Standard** (`~/.claude/lab-standard/STANDARD.md`). The map for both
humans and AI agents is **[AGENTS.md](AGENTS.md)** — read it first. In short:

- `src/{{PKG}}/` — reusable library code
- `experiments/exp-NNNN_slug/` — one self-contained folder per run (code + config + outputs + provenance)
- `experiments/INDEX.md` — registry of everything tried, and its outcome
- `notebooks/` — exploration only
- `docs/decisions/` — why things are the way they are (ADRs)
- `data/raw/` — read-only inputs (git-ignored; real data lives at the path in config)

## Where the data lives
{{DATA_LOCATION: absolute path on shared store / HPC scratch, and how to obtain it.}}
