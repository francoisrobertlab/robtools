#!/bin/bash
#SBATCH --account=def-robertf
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=12
#SBATCH --mem=48G
#SBATCH --mail-type=NONE
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
robtools bowtie2 "${args[@]}"
