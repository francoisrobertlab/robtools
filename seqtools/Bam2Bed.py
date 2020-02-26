from distutils.command.check import check
import logging
import os
import subprocess

import click
import pandas as pd
from seqtools.bed import Bed


@click.command()
@click.option('--samples', '-s', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--threads', '-t', default=1, show_default=True,
              help='Number of threads used to process data per sample.')
@click.option('--index', '-i', type=int, default=None,
              help='Index of sample to process in samples file.')
def main(samples, threads, index):
    '''Converts BAM file to BED for samples.'''
    logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    sample_names = pd.read_csv(samples, header=None, sep='\t', comment='#')[0]
    if index != None:
        sample_names = [sample_names[index]]
    for sample in sample_names:
        bam2bed(sample, threads)


def bam2bed(sample, threads=None):
    '''Converts BAM file to BED for a single sample.'''
    print ('Converting BAM to BED for sample {}'.format(sample))
    bam = sample + '.bam'
    bedpe = sample + '.bedpe'
    bam2bedpe(bam, bedpe, threads)
    bed_raw = sample + '.bed'
    bedpe2bed(bedpe, bed_raw)
    os.remove(bedpe)


def bam2bedpe(bam, bedpe, threads=None):
    '''Converts BAM file to BEDPE.'''
    print ('Converting BAM {} to BEDPE {}'.format(bam, bedpe))
    sort_output = bam + '.sort'
    cmd = ['samtools', 'sort', '-n']
    if not threads is None and threads > 1:
        cmd.extend(['--threads', str(threads - 1)])
    cmd.extend(['-o', sort_output, bam])
    logging.debug('Running {}'.format(cmd))
    subprocess.run(cmd, check=True)
    cmd = ['bedtools', 'bamtobed', '-bedpe', '-mate1', '-i', sort_output]
    logging.debug('Running {}'.format(cmd))
    with open(bedpe, 'w') as outfile:
        subprocess.run(cmd, stdout=outfile, check=True)
    os.remove(sort_output)


def bedpe2bed(bedpe, bed):
    '''Converts BEDPE file to BED by merging the paired reads.'''
    print ('Converting BAM BEDPE {} to BED {} by merging the paired reads'.format(bedpe, bed))
    merge_output = bedpe + '-merge.bed'
    with open(bedpe, 'r') as infile:
        with open(merge_output, 'w') as outfile:
            for line in infile:
                if line.startswith('track') or line.startswith('browser') or line.startswith('#'):
                    outfile.write(line)
                    continue
                columns = line.rstrip('\r\n').split('\t')
                start1 = int(columns[1])
                end1 = int(columns[2])
                start2 = int(columns[4])
                end2 = int(columns[5])
                start = min(start1, start2)
                end = max(end1, end2)
                outfile.write(columns[0])
                outfile.write('\t')
                outfile.write(str(start))
                outfile.write('\t')
                outfile.write(str(end))
                for i in range(6, 9):
                    outfile.write('\t')
                    outfile.write(columns[i])
                for i in range(10, len(columns)):
                    outfile.write('\t')
                    outfile.write(columns[i])
                outfile.write('\n')
    Bed.sort(merge_output, bed)
    os.remove(merge_output)


if __name__ == '__main__':
    main()
