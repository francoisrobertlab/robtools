#!/bin/bash
#SBATCH --account=def-robertf
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --mail-type=NONE
#SBATCH --output=download-%A_%a.out
#SBATCH --error=download-%A_%a.out

args=("$@")
args+=("--slow")
if [ ! -z "$SLURM_ARRAY_TASK_ID" ]
then
  args+=("-i" "$SLURM_ARRAY_TASK_ID")
fi

robtools download "${args[@]}"
