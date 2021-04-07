import logging
import os
import re
from statistics import mean, stdev
import subprocess

import click

from robtools import Split
from robtools.bed import Bed
from robtools.txt import Parser


@click.command()
@click.option('--samples', '-s', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--datasets', '-d', type=click.Path(), default='dataset.txt', show_default=True,
              help='Dataset name if first columns and sample names on following columns - tab delimited.')
@click.option('--bam-suffix', '-bs', default='', show_default=True,
              help='Suffix added to sample name for BAM containing low quality reads and duplicates.')
@click.option('--filtered-suffix', '-fs', default='-filtered', show_default=True,
              help='Suffix added to sample name for BAM without low quality reads but with duplicates.')
@click.option('--fragments/--no-fragments', default=False, show_default=True,
              help='Compute fragments statistics.')
@click.option('--fragment-suffix', '-es', default='', show_default=True,
              help='Suffix added to sample name for BED containing all fragments.')
@click.option('--output', '-o', type=click.Path(), default='statistics.txt', show_default=True,
              help='Output file were statistics are written.')
def statistics(samples, datasets, bam_suffix, filtered_suffix, fragment_suffix, fragments, output):
    '''Creates statistics file for samples.'''
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    statistics_samples(samples, datasets, bam_suffix, filtered_suffix, fragment_suffix, fragments, output)


def statistics_samples(samples='samples.txt', datasets='dataset.txt', bam_suffix='', filtered_suffix='-filtered', fragment_suffix='', fragments=False, output='statistics.txt'):
    '''Creates statistics file for samples.'''
    sample_names = Parser.first(samples)
    datasets_names = []
    if os.path.exists(datasets):
        datasets_names = Parser.first(datasets)
    compute_statistics(sample_names, datasets_names, bam_suffix, filtered_suffix, fragment_suffix, fragments, output)


def compute_statistics(samples, datasets, bam_suffix='', filtered_suffix='-filtered', fragment_suffix='', fragments=False, output='statistics.txt'):
    all_headers = headers(samples, datasets, fragments)
    splits = all_headers[1]
    samples_stats = []
    for sample in samples:
        sample_stats = sample_statistics(sample, splits, bam_suffix, filtered_suffix, fragment_suffix, fragments)
        samples_stats.append(sample_stats)
    if datasets:
        for dataset in datasets:
            sample_stats = sample_statistics(dataset, splits, bam_suffix, filtered_suffix, fragment_suffix, fragments)
            samples_stats.append(sample_stats)
    with open(output, 'w') as out:
        out.write('\t'.join(all_headers[0]))
        out.write('\n')
        for sample_stats in samples_stats:
            out.write('\t'.join([str(value) for value in sample_stats]))
            out.write('\n')


def headers(samples, datasets, fragments):
    '''Statistics headers'''
    headers = ['Sample', 'Total reads', 'Mapped reads', 'Deduplicated reads']
    if fragments:
        headers.extend(['Fragments average size', 'Fragments size std'])
    splits_headers = set()
    for sample in samples:
        splits_headers.update([split[len(sample) + 1:] for split in Split.splits(sample)])
    if datasets:
        for dataset in datasets:
            splits_headers.update([split[len(sample) + 1:] for split in Split.splits(sample)])
    splits_headers = [header for header in splits_headers]
    splits_headers.sort(key=Split.splitkey)
    headers.extend(splits_headers)
    return (headers, splits_headers)
    
    
def sample_statistics(sample, splits, bam_suffix='', filtered_suffix='-filtered', fragment_suffix='', fragments=False):
    '''Statistics of a single sample.'''
    print ('Computing statistics for sample {}'.format(sample))
    sample_stats = [sample]
    bam = sample + bam_suffix + '.bam'
    sample_stats.append(flagstat_total(bam) if os.path.isfile(bam) else '')
    bam_filtered = sample + filtered_suffix + '.bam'
    sample_stats.append(flagstat_total(bam_filtered) if os.path.isfile(bam_filtered) else '')
    bed = sample + fragment_suffix + '.bed'
    sample_stats.extend([Bed.count_bed(bed) * 2 if os.path.isfile(bed) else ''])
    if fragments:
        sizes = fragment_sizes(bed)
        sample_stats.append(mean(sizes))
        sample_stats.append(stdev(sizes))
    if splits:
        beds = [sample + fragment_suffix + '-' + split + '.bed' for split in splits]
        counts = [Bed.count_bed(sbed) if os.path.isfile(sbed) else '' for sbed in beds]
        sample_stats.extend(counts)
    return sample_stats


def flagstat_total(bam):
    cmd = ['samtools', 'flagstat', bam]
    logging.debug('Running {}'.format(cmd))
    output = subprocess.run(cmd, capture_output=True, check=True)
    return re.search('^\\d+', output.stdout.decode('utf-8')).group()


def fragment_sizes(bed):
    sizes = []
    with open(bed, 'r') as infile:
        for line in infile:
            if line.startswith('track') or line.startswith('browser') or line.startswith('#'):
                continue
            columns = line.rstrip('\r\n').split('\t')
            size = abs(int(columns[2]) - int(columns[1]))
            sizes.append(size)
    return sizes


if __name__ == '__main__':
    statistics()
