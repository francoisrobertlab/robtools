from distutils.command.check import check
import logging
import os
import subprocess

import click
from robtools.seq import Fastq
from robtools.txt import Parser


@click.command()
@click.option('--samples', '-s', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.'
              ' An SRR id can be provided (tab-separated) to download the FASTQ file automatically, otherwise FASTQ file must be provided.')
@click.option('--fast/--slow', default=True, show_default=True,
              help='Use faster or slower but safer program for download.')
@click.option('--threads', '-e', default=6, show_default=True,
              help='Number of threads used for download.')
@click.option('--mem', '-m', default='100MB', show_default=True,
              help='Memory allocated for sorting download.')
@click.option('--index', '-i', type=int, default=None,
              help='Index of sample to process in samples file.')
def download(samples, fast, threads, mem, index):
    '''Download reads of all samples.'''
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    download_samples(samples, fast, threads, mem, index)


def download_samples(samples='samples.txt', fast=True, threads=None, mem='100MB', index=None):
    '''Download reads of all samples.'''
    sample_columns = Parser.columns(samples)
    if index != None:
        sample_columns = [sample_columns[index]]
    for columns in sample_columns:
        sample = columns[0]
        srr = columns[1] if len(columns) > 1 else None
        download_sample(sample, srr, fast, threads, mem)


def download_sample(sample, srr, fast, threads, mem):
    '''Download reads of a sample.'''
    fastq = sample
    fastq_exists = Fastq.fastq(fastq, 1)
    if fastq_exists is None and srr:
        print ('Downloading FASTQ for sample {} with SRR {}'.format(sample, srr))
        fastq1 = fastq + '_1.fastq'
        fastq2 = fastq + '_2.fastq'
        srr_output1 = srr + '_1.fastq'
        srr_output2 = srr + '_2.fastq'
        cmd = ['fasterq-dump', '--split-files', '--threads', str(threads), '--mem', mem, srr]
        if not fast:
            cmd = ['fastq-dump', '--split-files', srr]
        logging.debug('Running {}'.format(cmd))
        subprocess.run(cmd, check=True)
        os.rename(srr_output1, fastq1)
        if os.path.isfile(srr_output2):
            os.rename(srr_output2, fastq2)


if __name__ == '__main__':
    download()
