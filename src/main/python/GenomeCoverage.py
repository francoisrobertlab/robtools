from functools import partial
import logging
from multiprocessing import Pool
import os
import subprocess

import FullAnalysis
import SplitBed
import click

BASE_SCALE = 1000000


@click.command()
@click.option('--samples', '-s', type=click.Path(exists=True), default='samples.txt',
              help='Sample names listed one sample name by line.')
@click.option('--sizes', '-S', type=click.Path(exists=True), default='sacCer3.chrom.sizes',
              help='Size of chromosomes.')
@click.option('--poolThreads', '-T', default=2,
              help='Samples to process in parallel.')
def main(samples, sizes, poolthreads):
    '''Compute genome coverage on samples.'''
    logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    samples_names = FullAnalysis.first_column(samples)
    with Pool(poolthreads) as pool:
        pool.map(partial(genome_coverage, sizes=sizes), samples_names)


def genome_coverage(sample, sizes):
    '''Compute genome coverage on a single sample.'''
    print ('Compute genome coverage on sample {}'.format(sample))
    do_genome_coverage(sample, sizes)
    splits = SplitBed.splits(sample)
    for split in splits:
        do_genome_coverage(split, sizes)


def do_genome_coverage(sample, sizes):
    bed_raw = sample + "-raw.bed"
    bed_ignore_strand = sample + "-istrand.bed"
    ignore_strand(bed_raw, bed_ignore_strand)
    count = count_bed(bed_ignore_strand)
    scale = BASE_SCALE / max(count, 1)
    bed = sample + '.bed'
    bigwig = sample + '.bw'
    coverage(bed_ignore_strand, bed, sizes, sample, scale)
    os.remove(bed_ignore_strand)
    bedgraph_to_bigwig(bed, bigwig, sizes)


def ignore_strand(bed, output):
    '''Resize annotations to 1 positioned at the center.'''
    with open(bed, "r") as infile, open(output, "w") as outfile:
        for line in infile:
            if line.startswith('track') or line.startswith('browser') or line.startswith('#'):
                outfile.write(line)
                continue
            columns = line.rstrip('\r\n').split('\t')
            if len(columns) >= 6:
                outfile.write('\t'.join(columns))
                outfile.write("\n")
                columns[5] = '+' if columns[5] == '-' else '-'
                outfile.write('\t'.join(columns))
                outfile.write("\n")


def count_bed(bed, strand=None):
    '''Counts number of entry in BED, can be limited to a specific strand.'''
    count = 0
    with open(bed, "r") as infile:
        for line in infile:
            if line.startswith('track') or line.startswith('browser') or line.startswith('#'):
                continue
            if strand is None:
                count += 1
            else:
                columns = line.rstrip('\r\n').split('\t')
                if len(columns) >= 6 and columns[5] == strand:
                    count += 1
    return count


def coverage(bed_input, bed_output, sizes, sample, scale=None, strand=None):
    '''Compute genome coverage.'''
    coverage_output = bed_input + '.cov'
    cmd = ['bedtools', 'genomecov', '-bg', '-5', '-i', bed_input, '-g', sizes]
    if not scale is None:
        cmd.extend(['-scale', str(scale)]) 
    if not strand is None:
        cmd.extend(['-strand', strand]) 
    logging.debug('Running {}'.format(cmd))
    with open(coverage_output, "w") as outfile:
        subprocess.call(cmd, stdout=outfile)
    if not os.path.isfile(coverage_output):
        raise AssertionError('Error when computing genome coverage on ' + bed_input)
    sort_output = bed_input + '.sort'
    cmd = ['bedtools', 'sort', '-i', coverage_output]
    logging.debug('Running {}'.format(cmd))
    with open(sort_output, "w") as outfile:
        subprocess.call(cmd, stdout=outfile)
    if not os.path.isfile(sort_output):
        raise AssertionError('Error when sorting BED ' + coverage_output)
    os.remove(coverage_output)
    track = 'track type=bedGraph name="' + sample + '"'
    if not strand is None:
        track += ' Minus' if strand == '-' else ' Plus'
    with open(sort_output, "r") as infile, open(bed_output, "w") as outfile:
        outfile.write(track + '\n')
        outfile.writelines(infile)
    os.remove(sort_output)


def empty_bed(bed_output, sample, strand=None):
    '''Create an empty BED file.'''
    track = 'track type=bedGraph name="' + sample + '"'
    if not strand is None:
        track += ' Minus' if strand == '-' else ' Plus'
    with open(bed_output, "w") as outfile:
        outfile.write(track + '\n')


def bedgraph_to_bigwig(bed, bigwig, sizes):
    '''Converts bedgraph file to bigwig.'''
    cmd = ['bedGraphToBigWig', bed, sizes, bigwig]
    logging.debug('Running {}'.format(cmd))
    subprocess.call(cmd)
    if not os.path.isfile(bigwig):
        raise AssertionError('Error when converting BED to BIGWIG ' + bed)


if __name__ == '__main__':
    main()
