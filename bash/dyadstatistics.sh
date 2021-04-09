#!/bin/bash
#SBATCH --account=def-robertf
#SBATCH --mem=16G
#SBATCH --mail-type=NONE
#SBATCH --output=dyadstatistics-%A.out
#SBATCH --error=dyadstatistics-%A.out

args=("$@")

mnasetools dyadstatistics "${args[@]}"
