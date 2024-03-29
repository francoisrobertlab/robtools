# Genome coverage using spiking

:link: *[Connecting to Compute Canada server](connect.md)*

:pill: Load the `robtools` module before running any command in this page

```shell
module load StdEnv/2018.3
module load robtools
```

#### Steps

* [Align FASTQ files with spiked genome](#align-fastq-files-with-spiked-genome)
* [Filter reads](#filter-reads-to-remove-poorly-map-reads-and-duplicates)
* [Merge samples into dataset](#merge-dataset-samples-data)
* [Convert BAM to BED](#convert-bam-files-to-fragment-bed-files)
* [Genome coverage](#genome-coverage)

## Align FASTQ files with spiked genome

### Download the FASTA file of the spiked genome and chromosomes size

:bulb: Instructions are for S. pombe as spiked genome

1. Go to the [PomBase](https://www.pombase.org)
2. Select "Download" -> "Dataset" -> "Genome sequence and features" -> "Genome sequence (ftp)"
3. Download the FASTA file for all chromosomes
4. [Upload the files to Compute Canada server in the same folder of the dataset files](upload.md)

### Run bowtie 2 or bwa

#### bowtie2

```shell
bowtie2-build Schizosaccharomyces_pombe_all_chromosomes.fa Schizosaccharomyces_pombe_all_chromosomes.fa.index
sbatch bowtie2.sh -x Schizosaccharomyces_pombe_all_chromosomes.fa.index -os -pombe
```

:bulb: To prevent out of memory errors, use `--array` argument for `sbatch`, see [sbatch](sbatch.md)

#### bwa

```shell
bwa index Schizosaccharomyces_pombe_all_chromosomes.fa
sbatch bwa.sh --fasta Schizosaccharomyces_pombe_all_chromosomes.fa -os -pombe
```

:bulb: To prevent out of memory errors, use `--array` argument for `sbatch`, see [sbatch](sbatch.md)

## Filter reads to remove poorly map reads and duplicates

```shell
sbatch filterbam.sh -is -pombe -os -pombe
```

:bulb: To prevent out of memory errors, use `--array` argument for `sbatch`, see [sbatch](sbatch.md)

## Merge dataset samples data

```shell
sbatch mergebam.sh --suffix -pombe-dedup
```

## Convert BAM files to fragment BED files

```shell
sbatch bam2bed.sh -is -pombe-dedup -os -pombe
sbatch bam2bed.sh -s dataset.txt -is -pombe-dedup -os -pombe
```

:bulb: The previous commands can be called simultaneously

## Genome coverage

:bulb: Adapt the parameters to match those of your analysis

```shell
sbatch genomecov.sh -g sacCer3.chrom.sizes -is -forcov -os -pombe-cov --spike-suffix -pombe
sbatch genomecov.sh -s dataset.txt -g sacCer3.chrom.sizes -is -forcov -os -pombe-cov --spike-suffix -pombe
```

:bulb: The previous commands can be called simultaneously
