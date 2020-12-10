from distutils.command.check import check
import logging
import os
import subprocess
import tempfile

import click
from robtools.seq import Fastq
from robtools.txt import Parser


@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('--samples', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--fasta', type=click.Path(exists=True), default='sacCer3.fa', show_default=True,
              help='FASTA file used for alignment.')
@click.option('--threads', '-t', default=1, show_default=True,
              help='Number of threads used to process data per sample.')
@click.option('--output-suffix', '-os', default='', show_default=True,
              help='Suffix added to sample name in BAM filename for output.')
@click.option('--index', type=int, default=None,
              help='Index of sample to process in samples file.')
@click.argument('bwa_args', nargs=-1, type=click.UNPROCESSED)
def bwa(samples, fasta, threads, output_suffix, index, bwa_args):
    '''Align samples using bwa program.'''
    logging.basicConfig(filename='seqtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    bwa_samples(samples, fasta, threads, output_suffix, index, bwa_args)


def bwa_samples(samples='samples.txt', fasta='sacCer3.fa', threads=None, output_suffix='', index=None, bwa_args=()):
    '''Align samples using bwa program.'''
    sample_names = Parser.first(samples)
    if index != None:
        sample_names = [sample_names[index]]
    for sample in sample_names:
        bwa_sample(sample, fasta, threads, output_suffix, bwa_args)


def bwa_sample(sample, fasta, threads=None, output_suffix='', bwa_args=()):
    '''Align one sample using bwa program.'''
    print ('Running BWA on sample {}'.format(sample))
    fastq1 = Fastq.fastq(sample, 1)
    if fastq1 is None:
        raise AssertionError('Cannot find FASTQ files for sample ' + sample)
    fastq2 = Fastq.fastq(sample, 2)
    paired = fastq2 is not None and os.path.isfile(fastq2)
    bam = sample + output_suffix + '.bam'
    run_bwa(fastq1, fastq2, fasta, bam, threads, bwa_args)


def bwa_index(fasta):
    '''Run BWA on FASTQ files.'''
    bwa_index_cmd = ['bwa', 'index', fasta]
    logging.debug('Running {}'.format(bwa_index_cmd))
    subprocess.run(bwa_index_cmd, check=True)


def run_bwa(fastq1, fastq2, fasta, bam_output, threads=None, bwa_args=()):
    '''Run BWA on FASTQ files.'''
    sam_output_o, sam_output = tempfile.mkstemp(suffix='.sam')
    cmd = ['bwa', 'mem'] + list(bwa_args)
    if not threads is None and threads > 1:
        cmd.extend(['-t', str(threads)])
    cmd.extend(['-o', sam_output, fasta, fastq1])
    if fastq2 is not None and os.path.isfile(fastq2):
        cmd.append(fastq2)
    logging.debug('Running {}'.format(cmd))
    subprocess.run(cmd, check=True)
    view_bam_o, view_bam = tempfile.mkstemp(suffix='.bam')
    cmd = ['samtools', 'view', '-b']
    if not threads is None and threads > 1:
        cmd.extend(['--threads', str(threads - 1)])
    cmd.extend(['-o', view_bam, sam_output])
    logging.debug('Running {}'.format(cmd))
    subprocess.run(cmd, check=True)
    os.remove(sam_output)
    sort(view_bam, bam_output, threads)
    os.remove(view_bam)


def sort(bam_input, bam_output, threads=None):
    '''Sort BAM file.'''
    cmd = ['samtools', 'sort']
    if not threads is None and threads > 1:
        cmd.extend(['--threads', str(threads - 1)])
    cmd.extend(['-o', bam_output, bam_input])
    logging.debug('Running {}'.format(cmd))
    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    bwa()
