#!/bin/bash
#SBATCH --account=def-robertf
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=20G
#SBATCH --mail-type=NONE
#SBATCH --output=merge-%A_%a.out
#SBATCH --error=merge-%A_%a.out

args=("$@")
if [ ! -z "$SLURM_ARRAY_TASK_ID" ]
then
  args+=("-i" "$SLURM_ARRAY_TASK_ID")
fi

robtools merge "${args[@]}"
