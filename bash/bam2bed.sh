#!/bin/bash
#SBATCH --account=def-robertf
#SBATCH --time=24:00:00
#SBATCH --array=0-0
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --mail-user=christian.poitras@ircm.qc.ca
#SBATCH --mail-type=ALL
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

bam2bed "${args[@]}"
