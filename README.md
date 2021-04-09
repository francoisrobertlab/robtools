# robtools: Tools to analyse next-generation sequencing data


## Install
Install requirements:
* [python version 3.7.4 or newer](https://www.python.org)
* [Git](https://git-scm.com)

Install robtools.

```
pip install git+https://git@github.com/francoisrobertlab/robtools.git
```


## Usage

The following executables are installed:
* robtools - tools used by most ChIP-seq analysis.
* mnasetools - tools specific to MNase-ChIP-seq analysis.
* chectools - tools specific to ChEC-seq analysis.

You can see the parameters details by using the `-h` parameter:

```
robtools -h
```


## Requirements

The following are required depending on the commands used:
* [perl](https://www.perl.org)
* [java](https://openjdk.java.net)
* [fastqc](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/)
* [trimmomatic](http://www.usadellab.org/cms/?page=trimmomatic)
* [bwa](http://bio-bwa.sourceforge.net)
* [bowtie2](http://bowtie-bio.sourceforge.net/bowtie2/index.shtml)
* [samtools](http://www.htslib.org)
* [bedtools](https://bedtools.readthedocs.io/en/latest/)
* [utilities from the UCSC Genome Browser](http://genome.ucsc.edu)
* [sra-toolkit from GeoArchive](https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?view=toolkit_doc)
* [vap](https://bitbucket.org/labjacquespe/vap/src/master/)
* [plot2do](https://github.com/rchereji/plot2DO)
