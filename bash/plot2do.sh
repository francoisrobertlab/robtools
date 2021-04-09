#!/bin/bash
#SBATCH --account=def-robertf
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=120G
#SBATCH --mail-type=NONE
#SBATCH --output=plot2do-%A_%a.out
#SBATCH --error=plot2do-%A_%a.out

args=("$@")
if [ ! -z "$SLURM_ARRAY_TASK_ID" ]
then
  args+=("-i" "$SLURM_ARRAY_TASK_ID")
fi

# Parameters for Martin.
# -t dyads -r Plus1 -L 400 -m 0.02
robtools plot2do "${args[@]}"
