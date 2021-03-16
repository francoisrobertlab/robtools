# MNase-ChIP-seq

:link: *[Connecting to Compute Canada server](connect.md)*

:pill: Load the `robtools` module before running any command in this page

```
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
* [Convert BAM to BED](#convert-bam-files-to-fragment-bed-files)
* [Keep only middle nucleotide](#keep-only-middle-nucleotide)
* [Genome coverage](#genome-coverage)
* [Statistics](#statistics)
* [Heatmaps of coverage over genes versus fragment size (Optional)](#heatmaps-of-coverage-over-genes-versus-fragment-size-optional)
* [Two-dimensional occupancy (2DO) plots (Optional)](#two-dimensional-occupancy-2do-plots-optional)
* [Distributions of MNase-ChIP-seq fragments relative to nucleosome dyads (Optional)](#distributions-of-mnase-chip-seq-fragments-relative-to-nucleosome-dyads-optional)


## Upload dataset files to Compute Canada

See [Uploading dataset files to Compute Canada server](upload.md)


## Download FASTA file of the genome

1. Go to the [UCSC Genome Browser downloads](http://hgdownload.soe.ucsc.edu/downloads.html)
2. Select organism
3. Select "*Genome sequence files and select annotations*"
4. Download the *2bit* file of the organism like *sacCer3.2bit* for Yeast
5. [Upload the files to Compute Canada server in the same folder of the dataset files](upload.md)
6. Convert the *2bit* file into a `FASTA` and `chromosome sizes` file using the following commands

```
twoBitToFa sacCer3.2bit sacCer3.fa
twoBitInfo sacCer3.2bit sacCer3.chrom.sizes
```


## Trim FASTQ files (Optional)

Run the following command

```
sbatch trimmomatic.sh --trimmers "ILLUMINACLIP:TruSeq3-PE-2.fa:2:30:10:2:keepBothReads LEADING:3 TRAILING:3 MINLEN:36"
```

:bulb: Before running the command, make sure the adapters are present in the file used in the `ILLUMINACLIP` trimmer, see [Trimmomatic adapters files](https://github.com/timflutre/trimmomatic/tree/master/adapters)

:bulb: To prevent out of memory errors, use `--array` argument for `sbatch`, see [sbatch](sbatch.md)


## Align FASTQ files with genome

Run the following commands

```
bowtie2-build sacCer3.fa sacCer3.fa.index
sbatch bowtie2.sh -x sacCer3.fa.index -X 1000 
```

:bulb: If you used Trimmomatic, add parameter `-is -paired` (or `-is trim` for single-ended reads) to the `bowtie2` command

:bulb: To prevent out of memory errors, use `--array` argument for `sbatch`, see [sbatch](sbatch.md)


## Filter reads to remove poorly map reads and duplicates

```
sbatch filterbam.sh
```

:bulb: To prevent out of memory errors, use `--array` argument for `sbatch`, see [sbatch](sbatch.md)


## Quality control check

```
sbatch fastqc.sh *.bam
```

Copy the HTML and ZIP files produced by FastQC on your local computer using an FTP software and check the result. [See the documentation for FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/)

:bulb: Check HTML files ending with "-dedup.bam" first!


## Merge dataset samples data

```
sbatch mergebam.sh --suffix -dedup
```


## Convert BAM files to fragment BED files

```
sbatch bam2bed.sh
sbatch bam2bed.sh -s dataset.txt
```

:bulb: The previous commands can be called simultaneously


## Keep only middle nucleotide

```
sbatch centerannotations.sh
sbatch centerannotations.sh -s dataset.txt
```

:bulb: The previous commands can be called simultaneously


## Genome coverage

```
sbatch genomecov.sh -g sacCer3.chrom.sizes -is -forcov
sbatch genomecov.sh -s dataset.txt -g sacCer3.chrom.sizes -is -forcov
```

:bulb: The previous commands can be called simultaneously


## Statistics

```
sbatch statistics.sh
```


## Heatmaps of coverage over genes versus fragment size (Optional)

### Upload VAP parameters and related files

Upload your VAP parameters file and related files to Compute Canada, see [VAP](https://bitbucket.org/labjacquespe/vap/src/master/) and [Uploading dataset files to Compute Canada server](upload.md)

An example of such files for yeast is available [here](mnase-chipseq/vap/sacCer3)

For yeast, you can copy the example files using these commands

```
curl https://raw.githubusercontent.com/francoisrobertlab/robtools/master/computecanada/mnase-chipseq/vap/sacCer3/vap_parameters.txt >> vap_parameters.txt
curl https://raw.githubusercontent.com/francoisrobertlab/robtools/master/computecanada/mnase-chipseq/vap/sacCer3/Group_AllLongGenes_TxSorted.txt >> Group_AllLongGenes_TxSorted.txt
curl https://raw.githubusercontent.com/francoisrobertlab/robtools/master/computecanada/mnase-chipseq/vap/sacCer3/sgdGeneAndOthers_UTR_TIF-seq_sacCer3_july_2018.txt >> sgdGeneAndOthers_UTR_TIF-seq_sacCer3_july_2018.txt
```

### Run the analysis

```
sbatch split.sh -s dataset.txt --binLength 10 --binMinLength 50 --binMaxLength 500
```

:bulb: To prevent out of memory errors when running `split.sh`, use `--array` argument for `sbatch`, see [sbatch](sbatch.md)

```
sbatch centerannotations.sh -s dataset.txt
sbatch genomecov.sh -s dataset.txt -g sacCer3.chrom.sizes -is -forcov
sbatch vap.sh -s dataset.txt -p vap_parameters.txt
remove-bins.sh
```


## Two-dimensional occupancy (2DO) plots (Optional)

```
module load plot2do
cd ~/projects/def-robertf/plot2DO
sbatch plot2do.sh -f ~/scratch/$dataset_name/dataset.txt -t dyads -r Plus1 -L 400 -m 0.02
```

`$dataset_name` is the folder containing the dataset files to be analyzed

:bulb: To prevent out of memory errors when running `plot2do.sh`, use `--array` argument for `sbatch`, see [sbatch](sbatch.md)


## Distributions of MNase-ChIP-seq fragments relative to nucleosome dyads (Optional)

:rat: For other organisms than yeast, please contact François Robert

### Copy dyad positions files

Copy [first dyad positions](mnase-chipseq/dyads/sacCer3/first_dyad.txt) and [second dyad positions](mnase-chipseq/dyads/sacCer3/second_dyad.txt) to Compute Canada

```
curl https://raw.githubusercontent.com/francoisrobertlab/robtools/master/computecanada/mnase-chipseq/dyads/sacCer3/first_dyad.txt >> first_dyad.txt
curl https://raw.githubusercontent.com/francoisrobertlab/robtools/master/computecanada/mnase-chipseq/dyads/sacCer3/second_dyad.txt >> second_dyad.txt
```

### Run the analysis

```
sbatch slowsplit.sh -s dataset.txt --binLength 11 --binMinLength 63 --binMaxLength 73
sbatch slowsplit.sh -s dataset.txt --binLength 11 --binMinLength 85 --binMaxLength 95
sbatch slowsplit.sh -s dataset.txt --binLength 11 --binMinLength 98 --binMaxLength 108
sbatch slowsplit.sh -s dataset.txt --binLength 11 --binMinLength 120 --binMaxLength 130
```

:bulb: The previous commands can be called simultaneously

```
sbatch centerannotations.sh -s dataset.txt
sbatch genomecov.sh -s dataset.txt -g sacCer3.chrom.sizes -is -forcov
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
