#!/bin/bash
#SBATCH --account=def-robertf
#SBATCH --time=24:00:00
#SBATCH --mem=8G
#SBATCH --mail-type=NONE
#SBATCH --output=statistics-%A.out
#SBATCH --error=statistics-%A.out

args=("$@")

robtools statistics "${args[@]}"
