import logging
import sys

import click
import pandas as pd
import pyBigWig as pbw

POSITIVE_STRAND = 1
NEGATIVE_STRAND = -1


@click.command()
@click.option('--genes', '-g', type=click.Path(exists=True), default='genes.txt', show_default=True,
              help='Genes information.')
@click.option('--signal', '-s', type=click.Path(exists=True), default='signal.bw', show_default=True,
              help='Dyad signal as a bigWig or bigBed file.')
@click.option('--dyad', '-i', type=int, default=2, show_default=True,
              help='Dyad index. Must be 2 right now.')
@click.option('--mind', '-d', type=int, default=141, show_default=True,
              help='Minimum distance from previous dyad.')
@click.option('--maxd', '-D', type=int, default=191, show_default=True,
              help='Maximum distance from previous dyad.')
@click.option('--output', '-o', type=click.Path(), default='genes-out.txt', show_default=True,
              help='Output file.')
def dyadposition(genes, signal, dyad, mind, maxd, output):
    '''Finds the most plausible dyad position.'''
    logging.basicConfig(filename='seqtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    dyad_position(genes, signal, dyad, mind, maxd, output)


def dyad_position(genes, signal, dyad, mind, maxd, output):
    '''Finds the most plausible dyad position.'''
    if dyad != 2:
        print >> sys.stderr, 'right now, dyad parameter must be 2'
        sys.exit(1)
    genes_info = pd.read_csv(genes, sep='\t', comment='#')
    bw = pbw.open(signal)
    diffd = maxd - mind
    next_nucleosomes = []
    for index, columns in genes_info.iterrows():
        chromosome = columns[1]
        strand = columns[4] == NEGATIVE_STRAND
        first_nucleosome = int(columns[7])
        start = first_nucleosome + (-(mind - 1) if strand else mind)
        end = start - diffd if strand else start + diffd
        next_nucleosome = highest_signal(bw, chromosome, min(start, end), max(start, end))
        next_nucleosomes.append(next_nucleosome[0])
    genes_info['+' + str(dyad) + ' nucleosome'] = next_nucleosomes
    genes_info.to_csv(output, sep='\t')


def highest_signal(bw, chromosome, start, end):
    '''Returns coordinate having the highest signal in the bigWig between specified coordinates'''
    intervals = bw.intervals(chromosome, start, end)
    if not intervals:
        return None
    max = intervals[0]
    for interval in intervals:
        if interval[2] > max[2]:
            max = interval
    return max


if __name__ == '__main__':
    dyadposition()
