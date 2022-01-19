# CheMap


#### Steps

* [Download FASTA file of the genome](#download-fasta-file-of-the-genome)
* [Trim FASTQ files (Optional)](#trim-fastq-files-optional)
* [Align FASTQ files](#align-fastq-files-with-genome)
* [Filter reads](#filter-reads-to-remove-poorly-map-reads-and-duplicates)
* [Quality control check](#quality-control-check)
* [Merge samples into dataset](#merge-dataset-samples-data)
* [Convert BAM to BED](#convert-bam-files-to-fragment-bed-files)
* [Keep only middle nucleotide](#keep-only-middle-nucleotide)
* [Genome coverage](#genome-coverage)
* [Statistics](#statistics)
* [Coverage for fragments of 51 bases](#coverage-for-fragments-of-51-bases)


## Download FASTA file of the genome

1. Go to the [UCSC Genome Browser downloads](http://hgdownload.soe.ucsc.edu/downloads.html)
2. Select organism
3. Select "*Genome sequence files and select annotations*"
4. Download the *2bit* file of the organism like *sacCer3.2bit* for Yeast
6. Convert the *2bit* file into a `FASTA` and `chromosome sizes` file using the following commands

```shell
twoBitToFa sacCer3.2bit sacCer3.fa
twoBitInfo sacCer3.2bit sacCer3.chrom.sizes
```


## Trim FASTQ files (Optional)

Run the following command

```shell
robtools trimmomatic --trimmers "ILLUMINACLIP:adapters.fa:2:30:10:2:keepBothReads LEADING:3 TRAILING:3 MINLEN:36"
```

:bulb: Before running the command, make sure the adapters are present in the file used in the `ILLUMINACLIP` trimmer,
see [Trimmomatic adapters files](https://github.com/timflutre/trimmomatic/tree/master/adapters)


## Align FASTQ files with genome

Run the following commands

```shell
bowtie2-build sacCer3.fa sacCer3.fa.index
robtools bowtie2 -x sacCer3.fa.index 
```

:bulb: If you used Trimmomatic, add parameter `-is -paired` (or `-is trim` for single-ended reads) to the `bowtie2`
command


## Filter reads to remove poorly map reads and duplicates

```shell
robtools filterbam
```


## Quality control check

```shell
fastqc *.bam
```

Copy the HTML and ZIP files produced by FastQC on your local computer using an FTP software and check the
result. [See the documentation for FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/)

:bulb: Check HTML files ending with "-dedup.bam" first!


## Merge dataset samples data

```shell
robtools mergebam --suffix -dedup
```


## Convert BAM files to fragment BED files

```shell
robtools bam2bed
robtools bam2bed -s dataset.txt
```


## Keep only middle nucleotide

```shell
robtools centerannotations
robtools centerannotations -s dataset.txt
```


## Genome coverage

```shell
robtools genomecov -g sacCer3.chrom.sizes -is -forcov
robtools genomecov -s dataset.txt -g sacCer3.chrom.sizes -is -forcov
```


## Statistics

Split is used to get per base fragments counts.

```shell
robtools split --binLength 1 --binMinLength 1 --binMaxLength 500
robtools statistics
```


### Coverage for fragments of 51 bases

```shell
robtools slowsplit -s dataset.txt --binLength 1 --binMinLength 51 --binMaxLength 52
rename 51-52.bed 51.bed *.bed
robtools centerannotations -s dataset.txt -is -51 -os -51-forcov
robtools genomecov -s dataset.txt -g sacCer3.chrom.sizes -is -51-forcov -os -51-cov
```
