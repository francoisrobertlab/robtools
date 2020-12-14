import os

import click
from robtools.txt import Parser


@click.command()
@click.option('--samples', '-s', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--suffix', default='', show_default=True,
              help='Suffix added to sample name.')
@click.option('--index', '-i', type=int, required=True,
              help='Index of sample to process in samples file.')
def printsample(samples, suffix, index):
    '''Print's sample's name at index of samples file.'''
    print_sample(samples, suffix, index)


def print_sample(samples='samples.txt', suffix='', index=0):
    '''Print's sample's name to output'''
    sample_names = Parser.first(samples)
    sample_names = [sample_names[index]]
    print (sample_names[0] + suffix)


if __name__ == '__main__':
    printsample()
