# ChIP-exo

:information_source: *[Connecting to Compute Canada server](connect.md)*

:bulb: Most `sbatch` commands can be optimized using `--array` argument, see [sbatch](sbatch.md)

#### Steps

* [Upload dataset files to Compute Canada](#upload-dataset-files-to-compute-canada)
* [Align FASTQ files](#align-fastq-files-with-genome)
* [Filter reads](#filter-reads-to-remove-poorly-map-reads-and-duplicates)
* [Quality control check](#quality-control-check)
* [Remove second mate](#remove-second-mate)
* [Convert BAM to BED](#convert-bam-files-to-fragment-bed-files)
* [Merge samples into dataset](#merge-dataset-samples-data)
* [Move annotations](#move-annotations)
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

### Run bwa

Run the following commands

```
bwa index sacCer3.fa
sbatch bwa.sh --fasta sacCer3.fa
```

:bulb: To prevent out of memory errors, use `--array` argument for `sbatch`, see [sbatch](sbatch.md)

## Filter reads to remove poorly map reads and duplicates

```
sbatch filterbam.sh
```

:bulb: To prevent out of memory errors, use `--array` argument for `sbatch`, see [sbatch](sbatch.md)

## Quality control check

### FastQC

```
sbatch fastqc.sh *.bam
```

Copy the HTML and ZIP files produced by FastQC on your local computer using an FTP software and check the result. [See the documentation for FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/)

:bulb: Check HTML files ending with "-dedup.bam" first!

### ChIPexoQual

```
module load chipexoqual
sbatch chipexoqual.sh --datasets dataset.txt 
```

Copy the PDF files produced by ChIPexoQual on your local computer using an FTP software and check the result. [See the documentation for ChIPexoQual](https://www.bioconductor.org/packages/release/bioc/vignettes/ChIPexoQual/inst/doc/vignette.html)

## Remove second mate

```
sbatch removesecondmate.sh
```

## Convert BAM files to fragment BED files

```
sbatch bam2bed.sh --unpaired -is -mate1
```

## Merge dataset samples data

```
sbatch merge.sh -m dataset.txt
```

## Move annotations

```
sbatch shiftannotations.sh -g sacCer3.chrom.sizes -m -6 -p 6
sbatch shiftannotations.sh -s dataset.txt -g sacCer3.chrom.sizes -m -6 -p 6
```

:bulb: The previous commands can be called simultaneously

## Genome coverage

```
sbatch genomecov.sh -g sacCer3.chrom.sizes -is -forcov -5
sbatch genomecov.sh -g sacCer3.chrom.sizes -is -forcov -5 -strand +
sbatch genomecov.sh -g sacCer3.chrom.sizes -is -forcov -5 -strand -
sbatch genomecov.sh -s dataset.txt -g sacCer3.chrom.sizes -is -forcov -5
sbatch genomecov.sh -s dataset.txt -g sacCer3.chrom.sizes -is -forcov -5 -strand +
sbatch genomecov.sh -s dataset.txt -g sacCer3.chrom.sizes -is -forcov -5 -strand -
```

:bulb: The previous commands can be called simultaneously

## Statistics

```
sbatch statistics.sh -m dataset.txt
```
