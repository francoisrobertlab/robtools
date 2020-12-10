from distutils.command.check import check
import logging
import os
import subprocess

import click
from robtools.txt import Parser


@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('--datasets', type=click.Path(exists=True), default='dataset.txt', show_default=True,
              help='Dataset name in first columns and sample names on following columns - tab delimited.')
@click.option('--suffix', default='', show_default=True,
              help='Suffix added to sample name in BAM filename for input.')
@click.option('--index', type=int, default=None,
              help='Index of sample to process in samples file.')
@click.argument('chipexoqual_args', nargs=-1, type=click.UNPROCESSED)
def chipexoqual(datasets, suffix, index, chipexoqual_args):
    '''Run ChIPexoQual on datasets.'''
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    chipexoqual_datasets(datasets, suffix, index, chipexoqual_args)


def chipexoqual_datasets(datasets='dataset.txt', suffix='', index=None, chipexoqual_args=()):
    '''Run ChIPexoQual on datasets.'''
    datasets_columns = Parser.columns(datasets)
    if index != None:
        datasets_columns = [datasets_columns[index]]
    for columns in datasets_columns:
        name = columns[0]
        samples = [sample for sample in columns[1:]]
        chipexoqual_dataset(name, samples, suffix, chipexoqual_args)


def chipexoqual_dataset(dataset, samples, suffix='', chipexoqual_args=()):
    '''Run ChIPexoQual on one dataset.'''
    print ('Running ChIPexoQual on dataset {}'.format(dataset))
    base = os.getenv('CHIPEXOQUAL_BASE')
    base = base + '/' if base else ''
    cmd = ['Rscript', base + 'chipexoqual.R', '-p', dataset + '_'] + list(chipexoqual_args) + [sample + suffix + '.bam' for sample in samples]
    logging.debug('Running {}'.format(cmd))
    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    chipexoqual()
