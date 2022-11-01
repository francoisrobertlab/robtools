#!/bin/bash
#SBATCH --account=def-robertf
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=24
#SBATCH --mem=8G
#SBATCH --mail-type=NONE
#SBATCH --output=pairs2hic-%A.out
#SBATCH --error=pairs2hic-%A.out

set -e

chrom_sizes=$1
if [[ ! -f "$chrom_sizes" ]]
then
  echo "You must supply chromosome sizes file as the first argument"
  exit 1
fi

if [ ! -z "$SLURM_CPUS_PER_TASK" ]
then
  threads=("--threads" "$SLURM_CPUS_PER_TASK")
fi

function join_by {
  local d=${1-} f=${2-}
  if shift 2; then
    printf %s "$f" "${@/#/$d}"
  fi
}

resolutions=$(robtools distillerresolutions)
resolutions=$(join_by ',' $resolutions)
echo "Resolutions are $resolutions"

pairs=$(find . -name "*.pairs.gz" | sort)
for pair in ${pairs};
do
  medium_format=$(awk '{print substr($0, 0, length-3)".tsv"}' <<< "$pair")
  hic=$(awk '{print substr($0, 0, length-3)".hic"}' <<< "$pair")
  echo ""
  echo "Converting $pair to HIC file $hic"
  gunzip -c "$pair" | \
      awk '{if ($0 !~ /^#/) {print $1"\t"($6!="+")"\t"$2"\t"$3"\t0\t"($7!="+")"\t"$4"\t"$5"\t1\t"$9"\t"$10}}' \
      > "$medium_format"
  java -jar "$JUICER_JAR" pre \
      -r "$resolutions" \
      "${threads[@]}" \
      "$medium_format" "$hic" "$1"
  rm "$medium_format"
done
