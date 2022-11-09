import logging
import subprocess
from pathlib import Path

import click

from robtools.txt import Parser


@click.command(context_settings=dict(ignore_unknown_options=True, ))
@click.option('--file', '-f', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--input-suffix', '-is', default='', show_default=True,
              help='Suffix added to sample name in BED filename for input.')
@click.option('--index', '-i', type=int, default=None, help='Index of sample to process in samples file.')
@click.argument('plot2do_args', nargs=-1, type=click.UNPROCESSED)
def plot2do(file, input_suffix, index, plot2do_args):
    '''Run plot2DO on samples.'''
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    plot2do_samples(file, input_suffix, index, plot2do_args)


def plot2do_samples(file, input_suffix='', index=None, plot2do_args=()):
    '''Run plot2DO on samples.'''
    file_parent = Path(file).parent
    sample_names = Parser.first(file)
    if index != None:
        sample_names = [sample_names[index]]
    for sample in sample_names:
        plot2do_sample(str(file_parent / sample), input_suffix, plot2do_args)


def plot2do_sample(sample, input_suffix='', plot2do_args=()):
    '''Run plot2DO on a single sample.'''
    print('Running plot2DO on sample {}'.format(sample))
    bed = sample + input_suffix + '.bed'
    cmd = ['Rscript', 'plot2DO.R'] + list(plot2do_args)
    cmd.extend(['-f', bed])
    logging.debug('Running {}'.format(cmd))
    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    plot2do()
