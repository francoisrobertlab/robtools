# ChIP-exo

:link: *[Connecting to Compute Canada server](connect.md)*

:pill: Load the `robtools` module before running any command in this page

```shell
module load robtools
```

#### Steps

* [Upload dataset files to Compute Canada](#upload-dataset-files-to-compute-canada)
* [Download FASTA file of the genome](#download-fasta-file-of-the-genome)
* [Trim FASTQ files (Optional)](#trim-fastq-files-optional)
* [Align FASTQ files](#align-fastq-files-with-genome)
* [Filter reads](#filter-reads-to-remove-poorly-map-reads-and-duplicates)
* [Quality control check](#quality-control-check)
* [Merge samples into dataset](#merge-dataset-samples-data)
* [Remove second mate](#remove-second-mate)
* [Convert BAM to BED](#convert-bam-files-to-fragment-bed-files)
* [Move annotations](#move-annotations)
* [Genome coverage](#genome-coverage)
* [Statistics](#statistics)


## Upload dataset files to Compute Canada

See [Uploading dataset files to Compute Canada server](upload.md)


## Download FASTA file of the genome

1. Go to the [UCSC Genome Browser downloads](http://hgdownload.soe.ucsc.edu/downloads.html)
2. Select organism
3. Select "*Genome sequence files and select annotations*"
4. Download the *2bit* file of the organism like *sacCer3.2bit* for Yeast
5. [Upload the files to Compute Canada server in the same folder of the dataset files](upload.md)
6. Convert the *2bit* file into a `FASTA` and `chromosome sizes` file using the following commands

```shell
twoBitToFa sacCer3.2bit sacCer3.fa
twoBitInfo sacCer3.2bit sacCer3.chrom.sizes
```


## Trim FASTQ files (Optional)

Run the following command

```shell
sbatch trimmomatic.sh --trimmers "ILLUMINACLIP:TruSeq3-PE-2.fa:2:30:10:2:keepBothReads LEADING:3 TRAILING:3 MINLEN:36"
```

:bulb: Before running the command, make sure the adapters are present in the file used in the `ILLUMINACLIP` trimmer, see [Trimmomatic adapters files](https://github.com/timflutre/trimmomatic/tree/master/adapters)

:bulb: To prevent out of memory errors, use `--array` argument for `sbatch`, see [sbatch](sbatch.md)


## Align FASTQ files with genome

Run the following commands

```shell
bwa index sacCer3.fa
sbatch bwa.sh --fasta sacCer3.fa
```

:bulb: If you used Trimmomatic, add parameter `-is -paired` (or `-is trim` for single-ended reads) to the `bwa` command

:bulb: To prevent out of memory errors, use `--array` argument for `sbatch`, see [sbatch](sbatch.md)


## Filter reads to remove poorly map reads and duplicates

```shell
sbatch filterbam.sh
```

:bulb: To prevent out of memory errors, use `--array` argument for `sbatch`, see [sbatch](sbatch.md)


## Quality control check

### FastQC

```shell
sbatch fastqc.sh *.bam
```

Copy the HTML and ZIP files produced by FastQC on your local computer using an FTP software and check the result. [See the documentation for FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/)

:bulb: Check HTML files ending with "-dedup.bam" first!

### ChIPexoQual

```shell
module load chipexoqual
sbatch chipexoqual.sh --datasets dataset.txt 
```

Copy the PDF files produced by ChIPexoQual on your local computer using an FTP software and check the result. [See the documentation for ChIPexoQual](https://www.bioconductor.org/packages/release/bioc/vignettes/ChIPexoQual/inst/doc/vignette.html)


## Merge dataset samples data

```shell
sbatch mergebam.sh --suffix -dedup
```


## Remove second mate

```shell
sbatch removesecondmate.sh
sbatch removesecondmate.sh -s dataset.txt
```

:bulb: The previous commands can be called simultaneously


## Convert BAM files to fragment BED files

```shell
sbatch bam2bed.sh --unpaired -is -mate1
sbatch bam2bed.sh -s dataset.txt --unpaired -is -mate1
```

:bulb: The previous commands can be called simultaneously


## Move annotations

```shell
sbatch shiftannotations.sh -g sacCer3.chrom.sizes -m -6 -p 6
sbatch shiftannotations.sh -s dataset.txt -g sacCer3.chrom.sizes -m -6 -p 6
```

:bulb: The previous commands can be called simultaneously


## Genome coverage

```shell
sbatch genomecov.sh -g sacCer3.chrom.sizes -is -forcov -5
sbatch genomecov.sh -g sacCer3.chrom.sizes -is -forcov -5 -strand +
sbatch genomecov.sh -g sacCer3.chrom.sizes -is -forcov -5 -strand -
sbatch genomecov.sh -s dataset.txt -g sacCer3.chrom.sizes -is -forcov -5
sbatch genomecov.sh -s dataset.txt -g sacCer3.chrom.sizes -is -forcov -5 -strand +
sbatch genomecov.sh -s dataset.txt -g sacCer3.chrom.sizes -is -forcov -5 -strand -
```

:bulb: The previous commands can be called simultaneously


## Statistics

```shell
sbatch statistics.sh
```
