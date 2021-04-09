#!/bin/bash
#SBATCH --account=def-robertf
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=30G
#SBATCH --mail-type=NONE
#SBATCH --output=bam2bed-%A_%a.out
#SBATCH --error=bam2bed-%A_%a.out

args=("$@")
if [ ! -z "$SLURM_ARRAY_TASK_ID" ]
then
  args+=("-i" "$SLURM_ARRAY_TASK_ID")
fi
if [ ! -z "$SLURM_CPUS_PER_TASK" ]
then
  args+=("-t" "$SLURM_CPUS_PER_TASK")
fi

robtools bam2bed "${args[@]}"
