# Robtools equivalent commands


* [Trim FASTQ files](#trim-fastq-files)
* [Align FASTQ files](#align-fastq-files-with-genome)
* [Filter reads](#filter-reads-to-remove-poorly-map-reads-and-duplicates)
* [Merge samples into dataset](#merge-dataset-samples-data)
* [Convert BAM to BED](#convert-bam-files-to-fragment-bed-files)
* [Keep only middle nucleotide](#keep-only-middle-nucleotide)
* [Genome coverage](#genome-coverage)


## Trim FASTQ files

```shell
robtools trimmomatic --trimmers "ILLUMINACLIP:adapters.fa:2:30:10:2:keepBothReads LEADING:3 TRAILING:3 MINLEN:36"
```

Equivalent if in paired-end and using trimmomatic version 0.39:
```shell
java -jar trimmomatic-0.39.jar PE "$sample"_R1.fastq.gz "$sample"_R2.fastq.gz \
"$sample"-paired_R1.fastq.gz "$sample"-unpaired_R1.fastq.gz \
"$sample"-paired_R2.fastq.gz "$sample"-unpaired_R2.fastq.gz \
ILLUMINACLIP:adapters.fa:2:30:10:2:keepBothReads LEADING:3 TRAILING:3 MINLEN:36
```


## Align FASTQ files with genome

```shell
robtools bowtie2 -x sacCer3.fa.index 
```

Equivalent if in paired-end:
```shell
bowtie2 -x sacCer3.fa.index -S "$sample".sam -1 "$sample"_R1.fastq.gz -2 "$sample"_R2.fastq.gz
samtools view -b "$sample".sam | samtools sort -o "$sample".bam
rm "$sample".sam
```


## Filter reads to remove poorly map reads and duplicates

```shell
robtools filterbam
```

Equivalent if in paired-end:
```shell
samtools view -b -F 2048 -F 256 -f 2 "$sample".bam | samtools sort -o "$sample"-filtered.bam
samtools sort -n -o "$sample"-forfixmate.bam "$sample"-filtered.bam
samtools fixmate -m "$sample"-forfixmate.bam "$sample"-fixmate.bam
samtools markdup -r "$sample"-fixmate.bam "$sample"-markdup.bam
samtools sort -o "$sample"-dedup.bam "$sample"-markdup.bam
rm "$sample"-forfixmate.bam "$sample"-fixmate.bam "$sample"-markdup.bam
```


## Merge dataset samples data

```shell
robtools mergebam --suffix -dedup
```

Equivalent if dataset has 2 samples:
```shell
samtools merge "$dataset"-dedup.bam "$sample1"-dedup.bam "$sample2"-dedup.bam
```


## Convert BAM files to fragment BED files

```shell
robtools bam2bed
robtools bam2bed -s dataset.txt
```

Equivalent if in paired-end:
```shell
samtools sort -n "$dataset"-dedup.bam | \
bedtools bamtobed -bedpe -mate1 | \
awk '{print $1"\t" if ($2 < $5) {print $2"\t"} else {print $5"\t"} if ($3 > $6) {print $3"\t"} else {print $6"\t"} print $7"\t"$8"\t"$9}' | \
sort -k 1,1 -k 2,2n -k 3,3n -o "$dataset".bed
```


## Keep only middle nucleotide

```shell
robtools centerannotations
robtools centerannotations -s dataset.txt
```

Equivalent:
```shell
awk '{print $1"\t"($2+$3)/2"\t"($2+$3)/2+1"\t"$4"\t"$5"\t"$6}' "$dataset".bed > "$dataset"-forcov.bed
```


## Genome coverage

```shell
robtools genomecov -g sacCer3.chrom.sizes -is -forcov
robtools genomecov -s dataset.txt -g sacCer3.chrom.sizes -is -forcov
```

Equivalent:
```shell
bedtools genomecov -i "$dataset"-forcov.bed -g sacCer3.chrom.sizes > "$dataset"-cov.bed
bedGraphToBigWig "$dataset"-cov.bed sacCer3.chrom.sizes "$dataset"-cov.bw
```
