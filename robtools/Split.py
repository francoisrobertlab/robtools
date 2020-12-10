import datetime
import logging
import os
import re
import subprocess
import tempfile

import click
from robtools.bed import Bed
from robtools.txt import Parser


@click.command()
@click.option('--samples', '-s', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--index', '-i', type=int, default=None,
              help='Index of sample to process in samples file.')
@click.option('--binLength', '-b', type=int, default=10, show_default=True,
              help='Split reads in bins by their length.')
@click.option('--binMinLength', '-l', type=int, default=100, show_default=True,
              help='First bin minimum length.')
@click.option('--binMaxLength', '-L', type=int, default=500, show_default=True,
              help='Last bin maximum length.')
def split(samples, index, binlength, binminlength, binmaxlength):
    '''Split BED files from samples based on lenght of annotations.'''
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    split_samples(samples, index, binlength, binminlength, binmaxlength)


def split_samples(samples='samples.txt', index=None, binlength=10, binminlength=100, binmaxlength=500):
    '''Split BED files from samples based on lenght of annotations.'''
    sample_names = Parser.first(samples)
    if index != None:
        sample_names = [sample_names[index]]
    for sample in sample_names:
        split_sample(sample, binlength, binminlength, binmaxlength)


def split_sample(sample, binlength, binminlength, binmaxlength):
    '''Split BED file from a single sample based on lenght of annotations.'''
    print ('Split BED file of sample {}'.format(sample))
    if binlength is not None:
        bed = sample + '.bed'
        bed_sort_o, bed_sort = tempfile.mkstemp(suffix='.bed')
        Bed.sort_bysize(bed, bed_sort)
        with open(bed_sort, 'r') as infile:
            line = infile.readline()
            length = annotation_length(line)
            for bin_start in range(binminlength, binmaxlength, binlength):
                bin_end = min(bin_start + binlength, binmaxlength)
                bin_temp_o, bin_temp = tempfile.mkstemp(suffix='.bed')
                bin_file = '{}-{}-{}.bed'.format(sample, bin_start, bin_end)
                print ('Splitting BED {} to BIN {}'.format(bed_sort, bin_file))
                with open(bin_temp_o, 'w') as outfile:
                    while line != '' and length < bin_end:
                        if length >= bin_start:
                            outfile.write(line)
                        line = infile.readline()
                        length = annotation_length(line)
                Bed.sort(bin_temp, bin_file)
                os.remove(bin_temp)
        os.remove(bed_sort)


def annotation_length(line):
    columns = line.rstrip('\r\n').split('\t')
    length = -1
    if len(columns) >= 3:
        length = int(columns[2]) - int(columns[1])
    return length


def splits(sample):
    '''Returns all splits for sample, sorted.'''
    regex = re.compile(sample + '-(\\d+)-\\d+\\.bed')
    files = os.listdir()
    beds = filter(regex.match, files)
    sample_splits = [bed[:-4] for bed in beds]
    sample_splits.sort(key=splitkey)
    return sample_splits


def splitkey(split):
    return int(re.search('(\\d+)-\\d+$', split).group(1))


if __name__ == '__main__':
    split()
