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

## Working with an AI assistant (Claude Code)
A Claude agent stays consistent across sessions here: it reads `AGENTS.md` + `experiments/INDEX.md`
first, reuses the shared code in `src/`, and is blocked from writing to the repo root or `data/raw/`.
You drive it in plain language:

- **Add to an existing experiment** — *"In `exp-0003`, also plot X grouped by Y."* → it edits inside
  that experiment's folder (reusing `src/`), saves outputs there, and updates that folder's notes.
- **Start a new experiment** — *"New experiment testing &lt;hypothesis&gt;."* → it runs `/new-experiment`,
  which scaffolds `experiments/exp-NNNN_<slug>/` **and auto-registers it in `experiments/INDEX.md`**,
  then asks you to confirm the hypothesis, writes `run.py` (reusing `src/`), and records how it ran.

You don't have to remind it to "update the index" — new experiments register themselves, and the
`just check` consistency check (run by pre-commit on every commit) blocks anything left undocumented.
What's genuinely yours to provide is the **hypothesis** and the **result write-up**.

## Where the data lives
{{DATA_LOCATION: absolute path on shared store / HPC scratch, and how to obtain it.}}
