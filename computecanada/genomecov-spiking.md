# Genome converage using spiking

:information_source: *[Connecting to Compute Canada server](connect.md)*

:bulb: Most `sbatch` commands can be optimized using `--array` argument, see [sbatch](sbatch.md)

#### Steps

* [Align FASTQ files with spiked genome](#align-fastq-files-with-spiked-genome)
* [Filter reads](#filter-reads-to-remove-poorly-map-reads-and-duplicates)
* [Merge samples into dataset](#merge-dataset-samples-data)
* [Convert BAM to BED](#convert-bam-files-to-fragment-bed-files)
* [Genome converage](#genome-coverage)

## Align FASTQ files with spiked genome

### Download the FASTA file of the spiked genome and chromosomes size

:bulb: Instructions are for S. pombe as spiked genome

1. Go to the [PomBase](https://www.pombase.org)
2. Select "Download" -> "Dataset" -> "Genome sequence and features" -> "Genome sequence (ftp)"
3. Download the FASTA file for all chromosomes
4. [Upload the files to Compute Canada server in the same folder of the dataset files](upload.md)

### Run bowtie 2 or bwa

#### bowtie2

```
bowtie2-build Schizosaccharomyces_pombe_all_chromosomes.fa Schizosaccharomyces_pombe_all_chromosomes.fa.index
sbatch bowtie2.sh -x Schizosaccharomyces_pombe_all_chromosomes.fa.index -os -pombe
```

:bulb: To prevent out of memory errors, use `--array` argument for `sbatch`, see [sbatch](sbatch.md)

#### bwa

```
bwa index Schizosaccharomyces_pombe_all_chromosomes.fa
sbatch bwa.sh --fasta Schizosaccharomyces_pombe_all_chromosomes.fa -os -pombe
```

:bulb: To prevent out of memory errors, use `--array` argument for `sbatch`, see [sbatch](sbatch.md)

## Filter reads to remove poorly map reads and duplicates

```
sbatch filterbam.sh -is -pombe -os pombe
```

:bulb: To prevent out of memory errors, use `--array` argument for `sbatch`, see [sbatch](sbatch.md)

## Merge dataset samples data

```
sbatch mergebam.sh --suffix -pombe-dedup
```

## Convert BAM files to fragment BED files

```
sbatch bam2bed.sh -is -pombe-dedup -os -pombe
sbatch bam2bed.sh -s dataset.txt -is -pombe-dedup -os -pombe
```

:bulb: The previous commands can be called simultaneously

## Genome coverage

:bulb: Adapt the parameters to match those of your analysis

```
sbatch genomecov.sh -g sacCer3.chrom.sizes -is -forcov -os -pombe-cov --spike-suffix -pombe
sbatch genomecov.sh -s dataset.txt -g sacCer3.chrom.sizes -is -forcov -os -pombe-cov --spike-suffix -pombe
```

:bulb: The previous commands can be called simultaneously
