# ChIP-seq

:information_source: *[Connecting to Compute Canada server](connect.md)*

:bulb: Most `sbatch` commands can be optimized using `--array` argument, see [sbatch](sbatch.md)

#### Steps

* [Upload dataset files to Compute Canada](#upload-dataset-files-to-compute-canada)
* [Align FASTQ files](#align-fastq-files-with-genome)
* [Filter reads](#filter-reads-to-remove-poorly-map-reads-and-duplicates)
* [Convert BAM to BED](#convert-bam-files-to-fragment-bed-files)
* [Merge samples into dataset](#merge-dataset-samples-data)
* [Genome converage](#genome-coverage)
* [Statistics](#statistics)

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
sbatch bowtie2.sh -x sacCer3.fa.index
```

:bulb: To prevent out of memory errors, use `--array` argument for `sbatch`, see [sbatch](sbatch.md)

## Filter reads to remove poorly map reads and duplicates

```
sbatch filterbam.sh
```

## Convert BAM files to fragment BED files

```
sbatch bam2bed.sh
```

## Merge dataset samples data

```
sbatch merge.sh -m dataset.txt
```

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
