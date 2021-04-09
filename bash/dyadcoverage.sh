#!/bin/bash
#SBATCH --account=def-robertf
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --mail-type=NONE
#SBATCH --output=dyadcoverage-%A_%a.out
#SBATCH --error=dyadcoverage-%A_%a.out

args=("$@")
if [ ! -z "$SLURM_ARRAY_TASK_ID" ]
then
  args+=("-i" "$SLURM_ARRAY_TASK_ID")
fi

mnasetools dyadcov "${args[@]}"
