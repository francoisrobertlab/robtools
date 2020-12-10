import logging
import os
import subprocess

import click
from robtools.txt import Parser

import robtools.Split as sb


@click.command()
@click.option('--samples', '-s', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--input-suffix', '-is', default='-dedup', show_default=True,
              help='Suffix added to sample name in BAM filename for input.')
@click.option('--output-suffix', '-os', default='-mate1', show_default=True,
              help='Suffix added to sample name in BAM filename for output.')
@click.option('--threads', '-t', default=1, show_default=True,
              help='Number of threads used to process data per sample.')
@click.option('--index', '-i', type=int, default=None,
              help='Index of sample to process in samples file.')
def removesecondmate(samples, input_suffix, output_suffix, threads, index):
    '''Removes second mate from BAM.'''
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    removesecondmate_samples(samples, input_suffix, output_suffix, threads, index)


def removesecondmate_samples(samples='samples.txt', input_suffix='-dedup', output_suffix='-mate1', threads=None, index=None):
    '''Removes second mate from BAM.'''
    sample_names = Parser.first(samples)
    if index != None:
        sample_names = [sample_names[index]]
    for sample in sample_names:
        removesecondmate_sample(sample, input_suffix, output_suffix, threads)


def removesecondmate_sample(sample, input_suffix='-dedup', output_suffix='-mate1', threads=None):
    '''Removes second mate from BAM for a single sample.'''
    print ('Removes second mate from BAM for sample {}'.format(sample))
    bam = sample + input_suffix + '.bam'
    mate1_bam = sample + output_suffix + '.bam'
    cmd = ['samtools', 'view']
    if not threads is None and threads > 1:
        cmd.extend(['--threads', str(threads - 1)])
    cmd.extend(['-f', '64', '-b', '-o', mate1_bam, bam])
    logging.debug('Running {}'.format(cmd))
    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    removesecondmate()
