from distutils.command.check import check
import logging
import os
import subprocess
import tempfile

import click
from robtools.bed import Bed
from robtools.txt import Parser


@click.command()
@click.option('--samples', '-s', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--paired/--unpaired', '-p/-u', default=True, show_default=True,
              help='Sample reads are paired')
@click.option('--threads', '-t', default=1, show_default=True,
              help='Number of threads used to process data per sample.')
@click.option('--input-suffix', '-is', default='-dedup', show_default=True,
              help='Suffix added to sample name in BAM filename for input.')
@click.option('--index', '-i', type=int, default=None,
              help='Index of sample to process in samples file.')
def bam2bed(samples, paired, threads, input_suffix, index):
    '''Converts BAM file to BED for samples.'''
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    bam2bed_samples(samples, paired, threads, input_suffix, index)


def bam2bed_samples(samples='samples.txt', paired=True, threads=None, input_suffix='', index=None):
    '''Converts BAM file to BED for samples.'''
    sample_names = Parser.first(samples)
    if index != None:
        sample_names = [sample_names[index]]
    for sample in sample_names:
        bam2bed_sample(sample, paired, threads, input_suffix)


def bam2bed_sample(sample, paired, threads=None, input_suffix=''):
    '''Converts BAM file to BED for a single sample.'''
    print ('Converting BAM to BED for sample {}'.format(sample))
    bam = sample + input_suffix + '.bam'
    bed = sample + '.bed'
    if paired:
        bedpe_o, bedpe = tempfile.mkstemp(suffix='.bedpe')
        bam2bedpe(bam, bedpe, threads)
        bedpe2bed(bedpe, bed)
        os.remove(bedpe)
    else:
        bam2bed_unpaired(bam, bed)


def bam2bed_unpaired(bam, bed):
    '''Converts BAM file to BED.'''
    conversion_output_o, conversion_output = tempfile.mkstemp(suffix='.bed')
    cmd = ['bedtools', 'bamtobed', '-i', bam]
    logging.debug('Running {}'.format(cmd))
    with open(conversion_output_o, 'w') as outfile:
        subprocess.run(cmd, stdout=outfile, check=True)
    Bed.sort(conversion_output, bed)
    os.remove(conversion_output)
    
    
def bam2bedpe(bam, bedpe, threads=None):
    '''Converts BAM file to BEDPE.'''
    print ('Converting BAM {} to BEDPE {}'.format(bam, bedpe))
    sort_output_o, sort_output = tempfile.mkstemp(suffix='.bam')
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
    merge_output_o, merge_output = tempfile.mkstemp(suffix='.bed')
    with open(bedpe, 'r') as infile:
        with open(merge_output_o, 'w') as outfile:
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
    bam2bed()
