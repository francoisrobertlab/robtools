import logging
import os
import subprocess

import click

import robtools.Split as sb
from robtools.txt import Parser


def validate_output_suffix(ctx, param, value):
    '''Validates that output suffix is different than input suffix'''
    input_suffix = ctx.params['input_suffix'] if 'input_suffix' in ctx.params else ''
    if value == input_suffix:
        raise click.BadParameter('output suffix "{}" must be different than input suffix'.format(value))
    else:
        return value


@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('--samples', '-s', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--input-suffix', '-is', default='', show_default=True,
              help='Suffix added to sample name in BED filename for input.')
@click.option('--output-suffix', '-os', callback=validate_output_suffix, default='-forcov', show_default=True,
              help='Suffix added to sample name in BED filename for output.')
@click.option('--index', '-i', type=int, default=None,
              help='Index of sample to process in samples file.')
@click.argument('bedtools_args', nargs=-1, type=click.UNPROCESSED)
def shiftannotations(samples, input_suffix, output_suffix, index, bedtools_args):
    '''Moves annotations contained in BED files.'''
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    shift_annotations_samples(samples, input_suffix, output_suffix, index, bedtools_args)


def shift_annotations_samples(samples='samples.txt', input_suffix='', output_suffix='-forcov', index=None, bedtools_args=()):
    '''Moves annotations contained in BED files.'''
    sample_names = Parser.first(samples)
    if index != None:
        sample_names = [sample_names[index]]
    for sample in sample_names:
        shift_annotations_sample(sample, input_suffix, output_suffix, bedtools_args)


def shift_annotations_sample(sample, input_suffix='', output_suffix='-forcov', bedtools_args=()):
    '''Moves annotations contained in BED file of sample.'''
    print ('Moves annotations contained in BED file of sample {}'.format(sample))
    bed = sample + input_suffix + '.bed'
    moved = sample + output_suffix + '.bed'
    cmd = ['bedtools', 'shift', '-i', bed] + list(bedtools_args)
    logging.debug('Running {}'.format(cmd))
    with open(moved, 'w') as outfile:
        subprocess.run(cmd, stdout=outfile, check=True)


if __name__ == '__main__':
    shiftannotations()
