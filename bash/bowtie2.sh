#!/bin/bash
#SBATCH --account=def-robertf
#SBATCH --time=24:00:00
#SBATCH --array=0-0
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --mail-user=christian.poitras@ircm.qc.ca
#SBATCH --mail-type=ALL
#SBATCH --output=bowtie2-%A_%a.out
#SBATCH --error=bowtie2-%A_%a.out

args=("$@")
if [ ! -z "$SLURM_ARRAY_TASK_ID" ]
then
  args+=("--index" "$SLURM_ARRAY_TASK_ID")
fi
if [ ! -z "$SLURM_CPUS_PER_TASK" ]
then
  args+=("--threads" "$SLURM_CPUS_PER_TASK")
fi

# Index FASTA file first
# bowtie2-build sacCer3.fa sacCer3.fa.index
#
# Recommended parameters for bowtie2
# -x sacCer3.fa.index -X 1000
runbowtie2 "${args[@]}"
