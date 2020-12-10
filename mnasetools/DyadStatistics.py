import logging
import os
import re

import click
import pandas as pd


@click.command()
@click.option('--minp', '-p', type=int, default=-75, show_default=True,
              help='Minimum position from dyad.')
@click.option('--maxp', '-P', type=int, default=75, show_default=True,
              help='Maximum position from dyad.')
@click.option('--output', '-o', type=click.Path(), default='dyad_statistics.txt', show_default=True,
              help='Output file were statistics are written.')
@click.option('--verbose', '-v', is_flag=True,
              help='Shows file name being processed.')
def dyadstatistics(minp, maxp, output, verbose):
    '''Creates statistics file for dyads.'''
    logging.basicConfig(filename='seqtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    dyad_statistics(minp, maxp, output, verbose)


def dyad_statistics(minp=-75, maxp=75, output='dyad_statistics.txt', verbose=False):
    '''Creates statistics file for dyads.'''
    all_genes_files = genes_files()
    statistics = pd.DataFrame(index=list(range(0, len(all_genes_files))), columns=['File', 'Reads', 'Genes'])
    for i in range(0, len(all_genes_files)):
        gene_file = all_genes_files[i]
        if verbose:
            print ('processing file {}'.format(gene_file))
        statistics.at[i, 'File'] = gene_file
        genes = pd.read_csv(gene_file, sep='\t', comment='#')
        position_headers = ['dyad position ' + str(p) for p in range(minp, maxp + 1)]
        reads = genes.loc[:, position_headers].sum(axis=1).sum()
        statistics.at[i, 'Reads'] = reads
        genes_with_reads = 0
        for j in genes.index.values:
            gene_sum = genes.loc[j, position_headers].sum()
            if gene_sum > 0:
                genes_with_reads += 1
        statistics.at[i, 'Genes'] = genes_with_reads
    statistics.to_csv(output, sep='\t', index=False)


def genes_files():
    regex = re.compile('.*-genes.txt')
    files = os.listdir()
    files = list(filter(regex.match, files))
    files.sort()
    return files


if __name__ == '__main__':
    dyadstatistics()
