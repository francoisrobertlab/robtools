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


@click.command()
@click.option('--samples', '-s', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--input-suffix', '-is', default='', show_default=True,
              help='Suffix added to sample name in BED filename for input.')
@click.option('--output-suffix', '-os', callback=validate_output_suffix, default='-forcov', show_default=True,
              help='Suffix added to sample name in BED filename for output.')
@click.option('--index', '-i', type=int, default=None,
              help='Index of sample to process in samples file.')
def ignorestrand(samples, input_suffix, output_suffix, index):
    '''Prepare BED file used for genome coverage on samples.'''
    logging.basicConfig(filename='seqtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ignore_strand_samples(samples, input_suffix, output_suffix, index)


def ignore_strand_samples(samples='samples.txt', input_suffix='', output_suffix='-forcov', index=None):
    '''Prepare BED file used for genome coverage on samples.'''
    sample_names = Parser.first(samples)
    if index != None:
        sample_names = [sample_names[index]]
    for sample in sample_names:
        ignore_strand_sample_splits(sample, input_suffix, output_suffix)


def ignore_strand_sample_splits(sample, input_suffix='', output_suffix='-forcov'):
    '''Prepare BED file used for genome coverage on a single sample.'''
    print ('Duplicate annotations on other strand on sample {}'.format(sample))
    ignore_strand_sample(sample, input_suffix, output_suffix)
    splits = sb.splits(sample)
    for split in splits:
        ignore_strand_sample(split, input_suffix, output_suffix)


def ignore_strand_sample(sample, input_suffix='', output_suffix='-forcov'):
    bed = sample + input_suffix + '.bed'
    bed_forcoverage = sample + output_suffix + '.bed'
    ignore_strand(bed, bed_forcoverage)


def ignore_strand(bed, output):
    '''Duplicate all annotations with opposed strand.'''
    with open(bed, 'r') as infile, open(output, 'w') as outfile:
        for line in infile:
            if line.startswith('track') or line.startswith('browser') or line.startswith('#'):
                outfile.write(line)
                continue
            columns = line.rstrip('\r\n').split('\t')
            if len(columns) >= 6:
                outfile.write('\t'.join(columns))
                outfile.write("\n")
                columns[5] = '+' if columns[5] == '-' else '-'
                outfile.write('\t'.join(columns))
                outfile.write("\n")


if __name__ == '__main__':
    ignorestrand()
