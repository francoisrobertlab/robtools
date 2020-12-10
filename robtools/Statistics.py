import logging
import os
import re
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
@click.option('--output', '-o', type=click.Path(), default='statistics.txt', show_default=True,
              help='Output file were statistics are written.')
def statistics(samples, datasets, output):
    '''Creates statistics file for samples.'''
    logging.basicConfig(filename='seqtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    statistics_samples(samples, datasets, output)


def statistics_samples(samples='samples.txt', datasets='dataset.txt', output='statistics.txt'):
    '''Creates statistics file for samples.'''
    sample_names = Parser.first(samples)
    datasets_names = []
    if os.path.exists(datasets):
        datasets_names = Parser.first(datasets)
    compute_statistics(sample_names, datasets_names, output)


def compute_statistics(samples, datasets, output):
    all_headers = headers(samples, datasets)
    splits = all_headers[1]
    samples_stats = []
    for sample in samples:
        sample_stats = sample_statistics(sample, splits)
        samples_stats.append(sample_stats)
    if datasets:
        for dataset in datasets:
            sample_stats = sample_statistics(dataset, splits)
            samples_stats.append(sample_stats)
    with open(output, 'w') as out:
        out.write('\t'.join(all_headers[0]))
        out.write('\n')
        for sample_stats in samples_stats:
            out.write('\t'.join([str(value) for value in sample_stats]))
            out.write('\n')


def headers(samples, datasets):
    '''Statistics headers'''
    headers = ['Sample', 'Total reads', 'Mapped reads', 'Deduplicated reads']
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
    
    
def sample_statistics(sample, splits):
    '''Statistics of a single sample.'''
    print ('Computing statistics for sample {}'.format(sample))
    sample_stats = [sample]
    bam = sample + '.bam'
    sample_stats.extend([flagstat_total(bam) if os.path.isfile(bam) else ''])
    bam_filtered = sample + '-filtered.bam'
    sample_stats.extend([flagstat_total(bam_filtered) if os.path.isfile(bam_filtered) else ''])
    bed = sample + '.bed'
    sample_stats.extend([Bed.count_bed(bed) * 2 if os.path.isfile(bed) else ''])
    if splits:
        beds = [sample + '-' + split + '.bed' for split in splits]
        counts = [Bed.count_bed(sbed) if os.path.isfile(sbed) else '' for sbed in beds]
        sample_stats.extend(counts)
    return sample_stats


def flagstat_total(bam):
    cmd = ['samtools', 'flagstat', bam]
    logging.debug('Running {}'.format(cmd))
    output = subprocess.run(cmd, capture_output=True, check=True)
    return re.search('^\\d+', output.stdout.decode('utf-8')).group()


if __name__ == '__main__':
    statistics()
