# MNase-ChIP-seq

:information_source: *[Connecting to Compute Canada server](connect.md)*

:bulb: Most `sbatch` commands can be optimized using `--array` argument, see [sbatch](sbatch.md)

#### Steps

* [Upload dataset files to Compute Canada](#upload-dataset-files-to-compute-canada)
* [Align FASTQ files](#align-fastq-files-with-genome)
* [Filter reads](#filter-reads-to-remove-poorly-map-reads-and-duplicates)
* [Convert BAM to BED](#convert-bam-files-to-fragment-bed-files)
* [Merge samples into dataset](#merge-dataset-samples-data)
* [Keep only middle nucleotide](#keep-only-middle-nucleotide)
* [Genome converage](#genome-coverage)
* [Statistics](#statistics)
* [Heatmaps of coverage over genes versus fragment size (Optional)](#heatmaps-of-coverage-over-genes-versus-fragment-size-optional)
* [Two-dimensional occupancy (2DO) plots (Optional)](#two-dimensional-occupancy-2do-plots-optional)
* [Distributions of MNase-ChIP-seq fragments relative to nucleosome dyads (Optional)](#distributions-of-mnase-chip-seq-fragments-relative-to-nucleosome-dyads-optional)

## Upload dataset files to Compute Canada

See [Uploading dataset files to Compute Canada server](upload.md)

## Align FASTQ files with genome

### Download the FASTA file of the genome and chromosomes size

1. Go to the [UCSC Genome Browser downloads](http://hgdownload.soe.ucsc.edu/downloads.html)
2. Select organism
3. Select "*Genome sequence files and select annotations*"
4. Download the *2bit* file of the organism like *sacCer3.2bit* for Yeast
4. Download the *chrom.sizes* file of the organism like *sacCer3.chrom.sizes* for Yeast
5. [Upload the files to Compute Canada server in the same folder of the dataset files](upload.md)
6. Convert the *2bit* file into a FASTA file using the following command

```
twoBitToFa sacCer3.2bit sacCer3.fa
```

### Run bowtie2

Run the following commands

```
bowtie2-build sacCer3.fa sacCer3.fa.index
sbatch bowtie2.sh -x sacCer3.fa.index -X 1000 
```

:bulb: To prevent out of memory errors, use `--array` argument for `sbatch`, see [sbatch](sbatch.md)

## Filter reads to remove poorly map reads and duplicates

```
sbatch filterbam.sh
```

:bulb: To prevent out of memory errors, use `--array` argument for `sbatch`, see [sbatch](sbatch.md)

## Convert BAM files to fragment BED files

```
sbatch bam2bed.sh
```

:bulb: To prevent out of memory errors, use `--array` argument for `sbatch`, see [sbatch](sbatch.md)

## Merge dataset samples data

```
sbatch merge.sh -m dataset.txt
```

## Keep only middle nucleotide

```
sbatch mnase-prepgenomecov.sh
sbatch mnase-prepgenomecov.sh -s dataset.txt
```

:bulb: The previous commands can be called simultaneously

## Genome coverage

```
sbatch genomecov.sh -S sacCer3.chrom.sizes
sbatch genomecov.sh -s dataset.txt -S sacCer3.chrom.sizes
```

:bulb: The previous commands can be called simultaneously

## Statistics

```
sbatch statistics.sh -m dataset.txt
```

## Heatmaps of coverage over genes versus fragment size (Optional)

Upload [VAP parameters file](mnase-chipseq/vap_parameters.txt) to Compute Canada, see [Uploading dataset files to Compute Canada server](upload.md)

```
sbatch split.sh -s dataset.txt --binLength 10 --binMinLength 50 --binMaxLength 500
sbatch mnase-prepgenomecov.sh -s dataset.txt
sbatch genomecov.sh -s dataset.txt -S sacCer3.chrom.sizes
sbatch vap.sh -s dataset.txt -p vap_parameters.txt
remove-bins.sh
```

## Two-dimensional occupancy (2DO) plots (Optional)

```
module load plot2do
cd ~/projects/def-robertf/plot2DO
sbatch plot2do.sh -f ~/scratch/$dataset_name/dataset.txt
```

`$dataset_name` is the folder containing the dataset files to be analyzed

## Distributions of MNase-ChIP-seq fragments relative to nucleosome dyads (Optional)

Upload [first dyad positions (sacCer3)](mnase-chipseq/sacCer3/first_dyad.txt) and [second dyad positions (sacCer3)](mnase-chipseq/sacCer3/second_dyad.txt) to Compute Canada, see [Uploading dataset files to Compute Canada server](upload.md)

For other organisms, contact François Robert

```
sbatch slowsplit.sh -s dataset.txt --binLength 11 --binMinLength 63 --binMaxLength 73
sbatch slowsplit.sh -s dataset.txt --binLength 11 --binMinLength 85 --binMaxLength 95
sbatch slowsplit.sh -s dataset.txt --binLength 11 --binMinLength 98 --binMaxLength 108
sbatch slowsplit.sh -s dataset.txt --binLength 11 --binMinLength 120 --binMaxLength 130
```

:bulb: The previous commands can be called simultaneously

```
sbatch mnase-prepgenomecov.sh -s dataset.txt
sbatch genomecov.sh -s dataset.txt -S sacCer3.chrom.sizes
```

:warning: The previous commands must be called sequentially

```
sbatch dyadcoverage.sh -s dataset.txt --smoothing 20 -g first_dyad.txt --suffix _first_dyad
sbatch dyadcoverage.sh -s dataset.txt --smoothing 20 -g second_dyad.txt --suffix _second_dyad
```

:bulb: The previous commands can be called simultaneously

```
sbatch fitgaussian.sh -s dataset.txt --svg --amin 0 --suffix _first_dyad
sbatch fitgaussian.sh -s dataset.txt --svg --amin 0 --suffix _second_dyad
sbatch fitdoublegaussian.sh -s dataset.txt --gaussian --svg --amin1 0 --amin2 0 --suffix _first_dyad
sbatch fitdoublegaussian.sh -s dataset.txt --gaussian --svg --amin1 0 --amin2 0 --suffix _second_dyad
```

:bulb: The previous commands can be called simultaneously

```
remove-bins.sh
```
