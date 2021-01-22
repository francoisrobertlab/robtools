#!/bin/bash
#SBATCH --account=def-robertf
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=30G
#SBATCH --mail-user=christian.poitras@ircm.qc.ca
#SBATCH --mail-type=ALL
#SBATCH --output=siqchipbed-%A_%a.out
#SBATCH --error=siqchipbed-%A_%a.out

args=("$@")
if [ ! -z "$SLURM_ARRAY_TASK_ID" ]
then
  args+=("--index" "$SLURM_ARRAY_TASK_ID")
fi
if [ ! -z "$SLURM_CPUS_PER_TASK" ]
then
  args+=("--threads" "$SLURM_CPUS_PER_TASK")
fi

robtools siqchip "${args[@]}"
