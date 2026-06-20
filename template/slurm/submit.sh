#!/bin/bash
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=08:00:00
# NOTE: --job-name / --output / --error are set by `just submit` so logs land inside the
# experiment folder. Adjust the resource lines above per experiment as needed.

set -euo pipefail
EXP="${1:?usage: submit.sh <exp-id>}"

# --- environment (edit to match your cluster) ---
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate {{ENV}}

cd "$SLURM_SUBMIT_DIR"
echo "host=$(hostname) job=${SLURM_JOB_ID:-NA} exp=${EXP}"

# Same entry point as `just run`, so local and HPC runs are identical and equally reproducible.
python "experiments/${EXP}/run.py" --config "experiments/${EXP}/config.yaml"
