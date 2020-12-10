import logging
import math
import os

import click
from numpy import mean

import matplotlib.pyplot as plt
import pandas as pd
import pyBigWig as pbw
import robtools.Split as sb
from robtools.txt import Parser

POSITIVE_STRAND = '+'
NEGATIVE_STRAND = '-'


@click.command()
@click.option('--samples', '-s', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--genes', '-g', type=click.Path(exists=True), default='genes.txt', show_default=True,
              help='Genes information with format <spacer text> <chromosome> <Gene Name> <TSS> <Strand> <TES> <Dyad Position>.')
@click.option('--selection', type=click.Path(exists=True), default=None, show_default=True,
              help='VAP selection_path file.')
@click.option('--absolute/--relative', '-a/-r', default=False, show_default=True,
              help='Use absolute or relative number of reads in plots')
@click.option('--minp', '-p', type=int, default=-75, show_default=True,
              help='Minimum position from dyad.')
@click.option('--maxp', '-P', type=int, default=75, show_default=True,
              help='Maximum position from dyad.')
@click.option('--smoothing', '-S', type=int, default=None,
              help='Smooth the signal by averaging on smoothing window.')
@click.option('--suffix', default=None,
              help='Suffix to append to sample name. Suffix is ignore for input if file does not exists - suffix is still applied to output.')
@click.option('--index', '-i', type=int, default=None,
              help='Index of sample to process in samples file.')
def dyadcov(samples, genes, selection, absolute, minp, maxp, smoothing, suffix, index):
    '''Finds the distribution of ditances between fragments and dyad.'''
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    dyad_coverage(samples, genes, selection, absolute, minp, maxp, smoothing, suffix, index)


def dyad_coverage(samples, genes='genes.txt', selection=None, absolute=False, minp=-75, maxp=75, smoothing=None, suffix=None, index=None):
    '''Finds the distribution of ditances between fragments and dyad.'''
    genes_info = pd.read_csv(genes, sep='\t', comment='#')
    genes_info = genes_info.loc[genes_info[genes_info.columns[6]] != -1]
    if selection:
        selection_genes = Parser.first(selection)
        genes_info = genes_info[genes_info[genes_info.columns[2]].isin(selection_genes)]
    sample_names = Parser.first(samples)
    if index != None:
        sample_names = [sample_names[index]]
    for sample in sample_names:
        dyad_coverage_sample(sample, genes_info, absolute, minp, maxp, suffix, smoothing)
        splits = sb.splits(sample)
        for split in splits:
            dyad_coverage_sample(split, genes_info, absolute, minp, maxp, suffix, smoothing)


def dyad_coverage_sample(sample, genes, absolute, minp, maxp, suffix=None, smoothing=None):
    '''Finds the distribution of ditances between fragments and dyad for a single sample.'''
    print ('Finds the distribution of ditances between fragments and dyad of sample {}'.format(sample))
    if not smoothing:
        smoothing = 0
    smoothing = math.ceil(smoothing / 2.0)
    coverage_bw = sample + '-cov.bw'
    if suffix and os.path.exists(sample + suffix + '-cov.bw'):
        coverage_bw = sample + suffix + '-cov.bw'
    bw = pbw.open(coverage_bw)
    distances = [[] for i in range(0, maxp - minp + smoothing * 2 + 1)]
    for index, columns in genes.iterrows():
        chromosome = columns[1]
        max_end = bw.chroms(chromosome)
        if not max_end:
            max_end = 0
        negative = columns[4] == NEGATIVE_STRAND
        theo_start = int(columns[6]) + minp - smoothing
        start = max(theo_start, 0)
        end = min(int(columns[6]) + maxp + smoothing + 1, max_end)
        distance = signal(bw, chromosome, start, end) if end > start else []
        if negative:
            distance.reverse()
        for i in range(0, maxp - minp + smoothing * 2 + 1):
            distance_index = i - (start - theo_start)
            value = distance[distance_index] if distance_index in range(0, len(distance)) else 0
            distances[i].append(value if value and not math.isnan(value) else 0)
    for i in range(0, maxp - minp + smoothing * 2 + 1):
        genes['dyad position ' + str(i + minp - smoothing)] = distances[i]
    genes_output = sample + (suffix if suffix else '') + '-genes.txt'
    genes.to_csv(genes_output, sep='\t', index=False)
    sums = pd.DataFrame(index=list(range(minp - smoothing, maxp + smoothing + 1)))
    sums['Frequency'] = [genes['dyad position ' + str(i)].sum() for i in range(minp - smoothing, maxp + smoothing + 1)]
    dyads = pd.DataFrame(index=list(range(minp, maxp + 1)), columns=['Frequency', 'Relative Frequency'])
    for i in range(minp, maxp + 1):
        dyads.at[i, 'Frequency'] = mean([sums.at[j, 'Frequency'] for j in range(i - smoothing, i + smoothing + 1)])
    frequency_sum = dyads['Frequency'].sum()
    for i in range(minp, maxp + 1):
        dyads.at[i, 'Relative Frequency'] = dyads.at[i, 'Frequency'] / frequency_sum
    dyad_output = sample + (suffix if suffix else '') + '-dyad.txt'
    dyads.to_csv(dyad_output, sep='\t')
    plot_dyad_coverage(sample, dyads, absolute, suffix)


def plot_dyad_coverage(sample, dyads, absolute, suffix=None):
    x = dyads.index.values
    yheader = 'Frequency' if absolute else 'Relative Frequency'
    plt.figure()
    plt.title(sample)
    plt.xlabel('Position relative to dyad (bp)')
    plt.ylabel('Frequency' if absolute else 'Relative Frequency')
    plt.xlim(x[0], x[len(x) - 1])
    plt.xticks(list(range(x[0], x[len(x) - 1] + 1, 25)))
    plt.plot(dyads.index.values, dyads[yheader].values, color='red')
    plot_output = sample + (suffix if suffix else '') + '-dyad.png'
    plt.savefig(plot_output)
    plt.clf()


def signal(bw, chromosome, start, end):
    '''Returns signal from bigWig'''
    return bw.values(chromosome, start, end)


if __name__ == '__main__':
    dyadcov()
