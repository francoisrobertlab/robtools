from distutils.command.check import check
import logging
import os
import subprocess
import tempfile

import click
from seqtools.seq import Fastq
from seqtools.txt import Parser


@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('--samples', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--threads', '-p', default=1, show_default=True,
              help='Number of threads used to process data per sample.')
@click.option('--index', type=int, default=None,
              help='Index of sample to process in samples file.')
@click.argument('bowtie_args', nargs=-1, type=click.UNPROCESSED)
def bowtie2(samples, threads, index, bowtie_args):
    '''Align samples using bowtie2 program.'''
    logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    bowtie_samples(samples, threads, index, bowtie_args)


def bowtie_samples(samples='samples.txt', threads=None, index=None, bowtie_args=()):
    '''Align samples using bowtie2 program.'''
    sample_names = Parser.first(samples)
    if index != None:
        sample_names = [sample_names[index]]
    for sample in sample_names:
        bowtie_sample(sample, threads, bowtie_args)


def bowtie_sample(sample, threads=None, bowtie_args=()):
    '''Align one sample using bowtie2 program.'''
    print ('Running bowtie2 on sample {}'.format(sample))
    fastq1 = Fastq.fastq(sample, 1)
    if fastq1 is None:
        raise AssertionError('Cannot find FASTQ files for sample ' + sample)
    fastq2 = Fastq.fastq(sample, 2)
    paired = fastq2 is not None and os.path.isfile(fastq2)
    bam = sample + '.bam'
    run_bowtie(fastq1, fastq2, bam, threads, bowtie_args)


def run_bowtie(fastq1, fastq2, bam_output, threads=None, bowtie_args=()):
    '''Run bowtie2 on FASTQ files.'''
    sam_output_o, sam_output = tempfile.mkstemp(suffix='.sam')
    cmd = ['bowtie2'] + list(bowtie_args)
    if not threads is None and threads > 1:
        cmd.extend(['-p', str(threads)])
    cmd.extend(['-S', sam_output])
    if fastq2 is not None and os.path.isfile(fastq2):
        cmd.extend(['-1', fastq1, '-2', fastq2])
    else:
        cmd.extend(['-U', fastq1])
    logging.debug('Running {}'.format(cmd))
    subprocess.run(cmd, check=True)
    cmd = ['samtools', 'view', '-b']
    if not threads is None and threads > 1:
        cmd.extend(['--threads', str(threads - 1)])
    cmd.extend(['-o', bam_output, sam_output])
    logging.debug('Running {}'.format(cmd))
    subprocess.run(cmd, check=True)
    os.remove(sam_output)


if __name__ == '__main__':
    bowtie2()
