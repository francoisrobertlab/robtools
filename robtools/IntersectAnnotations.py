from distutils.command.check import check
import logging
import os
import subprocess

import click
from robtools.txt import Parser


@click.command()
@click.option('--input', '-i', type=click.Path(exists=True),
              help='Bed input file containing all annotations.')
@click.option('--annotations', '-a', type=click.Path(exists=True),
              help='File containing annotation names.')
@click.option('--output', '-o', type=click.Path(),
              help='Bed output.')
def intersectannotations(input, annotations, output):
    '''Filter BED file to keep only annotations present in annotations.'''
    logging.basicConfig(filename='seqtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    genes = Parser.first(annotations)
    incolumns = Parser.columns(input)
    with open(output, 'w') as outfile:
        for columns in incolumns:
            if columns[3] in genes:
                outfile.write(str(columns[0]))
                for column in columns[1:]:
                    outfile.write('\t')
                    outfile.write(str(column))
                outfile.write('\n')


if __name__ == '__main__':
    intersectannotations()
