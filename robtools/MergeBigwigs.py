import logging
import math
import os
import tempfile

import click

import pyBigWig as pbw
from robtools.bed import Bed
from robtools.txt import Parser


@click.command()
@click.option('--datasets', '-d', type=click.Path(exists=True), default='dataset.txt', show_default=True,
              help='Dataset name if first columns and sample names on following columns - tab delimited.')
@click.option('--sizes', '-S', type=click.Path(exists=True), default='sacCer3.chrom.sizes', show_default=True,
              help='Size of chromosomes.')
@click.option('--index', '-i', type=int, default=None,
              help='Index of sample to process in samples file.')
def mergebw(datasets, sizes, index):
    '''Merge bigWig files related to samples.'''
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    merge_datasets(datasets, sizes, index)


def merge_datasets(datasets='dataset.txt', sizes='sacCer3.chrom.sizes', index=None):
    '''Merge bigWig files related to samples.'''
    datasets_columns = Parser.columns(datasets)
    if index != None:
        datasets_columns = [datasets_columns[index]]
    for columns in datasets_columns:
        name = columns[0]
        samples = [sample for sample in columns[1:]]
        merge_dataset(name, samples, sizes)

    
def merge_dataset(name, samples, sizes):
    '''Merge bigWig files related to samples.'''
    print ('Merging samples {} into dataset {}'.format(samples, name))
    sizes_columns = Parser.columns(sizes)
    bws = [pbw.open(sample + '.bw') for sample in samples]
    merge_temp_o, merge_temp = tempfile.mkstemp(suffix='.bed')
    with open(merge_temp_o, 'w') as output:
        output.write('track type=bedGraph name="' + name + '"\n')
        for size_columns in sizes_columns:
            chromosome = size_columns[0]
            size = int(size_columns[1])
            sums = [0] * size
            for bw in bws:
                bw_size = bw.chroms(chromosome) if bw.chroms(chromosome) else 0
                if bw_size == 0:
                    continue
                values = bw.values(chromosome, 0, min(size, bw_size))
                sums = [sums[i] + (values[i] if not math.isnan(values[i]) else 0) for i in range(0, min(size, bw_size))]
            for i in range(0, len(sums)):
                output.write(chromosome)
                output.write('\t')
                output.write(str(i))
                output.write('\t')
                output.write(str(i + 1))
                output.write('\t')
                output.write(str(sums[i]))
                output.write('\n')
    sort_temp_o, sort_temp = tempfile.mkstemp(suffix='.bed')
    Bed.sort(merge_temp, sort_temp)
    merged_bw = name + '.bw'
    Bed.bedgraph_to_bigwig(sort_temp, merged_bw, sizes)
    os.remove(sort_temp)
    os.remove(merge_temp)


if __name__ == '__main__':
    mergebw()
