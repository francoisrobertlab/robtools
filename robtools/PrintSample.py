import os

import click
from robtools.txt import Parser


@click.command()
@click.option('--samples', '-s', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--replicates/--hide-replicates', '-p/-u', default=False, show_default=True,
              help='Show all columns (replicates for dataset file) with additional suffix if specified')
@click.option('--suffix', default='', show_default=True,
              help='Suffix added to sample name.')
@click.option('--index', '-i', type=int, required=True,
              help='Index of sample to process in samples file.')
def printsample(samples, replicates, suffix, index):
    '''Print's sample's name at index of samples file.'''
    print_sample(samples, replicates, suffix, index)


def print_sample(samples='samples.txt', replicates=False, suffix='', index=0):
    '''Print's sample's name to output'''
    sample_names = Parser.columns(samples)
    sample_names = sample_names[index]
    if not replicates:
        sample_names = sample_names[:1]
    sample_names = [sample + suffix for sample in sample_names]
    print("\t".join(sample_names))


if __name__ == '__main__':
    printsample()
