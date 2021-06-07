import logging
import subprocess

import click
from robtools.txt import Parser


@click.command()
@click.option('--datasets', '-d', type=click.Path(exists=True), default='dataset.txt', show_default=True,
              help='Dataset name in first columns and sample names on following columns - tab delimited.')
@click.option('--suffix', '-s', default='', show_default=True,
              help='Suffix added to merge name and sample name in BAM filename.')
@click.option('--threads', '-t', default=1, show_default=True,
              help='Number of threads used to process data per sample.')
@click.option('--index', '-i', type=int, default=None,
              help='Index of sample to process in samples file.')
def mergebam(datasets, suffix, threads, index):
    '''Merge BAM files related to samples.'''
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    merge_datasets(datasets, suffix, threads, index)


def merge_datasets(datasets='dataset.txt', suffix='', threads=1, index=None):
    '''Merge BAM files related to samples.'''
    datasets_columns = Parser.columns(datasets)
    if index != None:
        datasets_columns = [datasets_columns[index]]
    for columns in datasets_columns:
        name = columns[0]
        samples = [sample for sample in columns[1:]]
        merge_dataset(name, samples, suffix, threads)


def merge_dataset(name, samples, suffix='', threads=1):
    '''Merge BAM files related to samples.'''
    print ('Merging samples {} into a single sample {}'.format(samples, name))
    for sample in samples:
        bam_input = sample + suffix + '.bam'
        cmd = ['samtools', 'index']
        if not threads is None and threads > 1:
            cmd.extend(['-@', str(threads - 1)])
        cmd.extend([bam_input])
        logging.debug('Running {}'.format(cmd))
        subprocess.run(cmd, check=True)
    bams_input = [sample + suffix + '.bam' for sample in samples]
    bam_output = name + suffix + '.bam'
    cmd = ['samtools', 'merge', '-f']
    if not threads is None and threads > 1:
        cmd.extend(['--threads', str(threads - 1)])
    cmd.extend([bam_output])
    cmd.extend(bams_input)
    logging.debug('Running {}'.format(cmd))
    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    merge()
