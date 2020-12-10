import logging
import re

import click
import pandas as pd

POSITIVE_STRAND = '+'
NEGATIVE_STRAND = '-'


@click.command()
@click.option('--genes', '-g', type=click.Path(exists=True), default='genes.txt', show_default=True,
              help='Genes information with format <spacer text> <chromosome> <Gene Name> <TSS> <Strand> <TES>.')
@click.option('--signal', '-s', type=click.Path(exists=True), default='signal.bed', show_default=True,
              help='Dyads most likely positions as WIG file with one track per gene in the order of the genes input.')
@click.option('--mind', '-d', type=int, default=50, show_default=True,
              help='Minimum distance from gene start.')
@click.option('--maxd', '-D', type=int, default=250, show_default=True,
              help='Maximum distance from gene start.')
@click.option('--output', '-o', type=click.Path(), default='genes-out.txt', show_default=True,
              help='Output file.')
def firstdyadposition(genes, signal, mind, maxd, output):
    '''Finds the most plausible position of first dyad for genes.'''
    first_dyad_position(genes, signal, mind, maxd, output)


def first_dyad_position(genes, signal, mind, maxd, output):
    '''Finds the most plausible position of first dyad for genes.'''
    logging.basicConfig(filename='FirstDyadPositionFinder.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    genes_info = pd.read_csv(genes, sep='\t', comment='#')
    tracks = read_tracks(signal)
    diffd = maxd - mind
    nucleosomes = []
    for index, columns in genes_info.iterrows():
        chromosome = columns[1]
        gene = columns[2]
        negative = columns[4] == NEGATIVE_STRAND
        start = int(columns[5] if negative else columns[3]) + (-mind if negative else mind)
        end = start - diffd if negative else start + diffd
        if gene not in tracks:
            logging.warning('no track for gene {}'.format(gene))
            nucleosomes.append(-1)
            continue
        track = tracks[gene]
        if negative:
            track.reverse()
        nucleosome = highest_signal(track, chromosome, min(start, end), max(start, end))
        nucleosomes.append(nucleosome[0] if nucleosome else -1)
    genes_info.columns = ['spacer', 'chromosome', 'gene', 'tss', 'strand', 'tes']
    genes_info['+1 nucleosome'] = nucleosomes
    genes_info.astype({'+1 nucleosome': 'int64'}).dtypes
    genes_info.to_csv(output, sep='\t', index=False)


def read_tracks(wig):
    '''Reads all tracks of wig and return an array of position/score'''
    trackname_regex = re.compile('name="([^"]*)"')
    tracks = {}
    track = []
    trackname = ''
    with open(wig) as input:
        for line in input:
            if line.startswith('fixedStep'):
                raise 'fixedStep not supported for signal file'
            if line.startswith('#') or line.startswith('browser') or line.startswith('variableStep') or line.startswith('fixedStep'):
                continue
            if line.startswith('track'):
                if track:
                    tracks[trackname] = track
                track = []
                match = trackname_regex.search(line)
                if match:
                    trackname = match.group(1)
                else:
                    logging.warning('"{}" does not have a name'.format(line))
                continue
            columns = line.rstrip('\r\n').split()
            position = int(columns[0])
            score = int(columns[1])
            track.append((position, score))
    return tracks


def highest_signal(track, chromosome, start, end):
    '''Returns coordinate having the highest signal between specified coordinates'''
    intervals = []
    for (position, score) in track:
        if position >= start and position < end:
            intervals.append((position, score))
    if not intervals:
        return None
    max = intervals[0]
    for interval in intervals:
        if interval[1] > max[1]:
            max = interval
    return max


if __name__ == '__main__':
    firstdyadposition()
