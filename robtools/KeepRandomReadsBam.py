import logging
import random
import tempfile

import click
import pysam

from robtools.bam import Bam
from robtools.txt import Parser


@click.command()
@click.option('--samples', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--count', type=int, default=10000000, show_default=True, help='Number of reads to keep.')
@click.option('--paired/--unpaired', '-p/-u', default=True, show_default=True, help='Sample reads are paired')
@click.option('--threads', '-t', type=int, default=1, show_default=True,
              help='Number of threads used to process data per sample.')
@click.option('--input-suffix', default='', show_default=True,
              help='Suffix to add to sample name to obtain input reads BAM filename.')
@click.option('--output-suffix', default='-random', show_default=True,
              help='Suffix added to sample name in output BAM filename.')
@click.option('--index', type=int, default=None, help='Index of sample to process in samples file.')
def keeprandomreadsbam(samples, count, paired, threads, input_suffix, output_suffix, index):
    """Keep count number of reads from BAM file."""
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    keeprandomreads_samples(samples, count, paired, threads, input_suffix, output_suffix, index)


def keeprandomreads_samples(samples, count=10000000, paired=True, threads=None, input_suffix='',
                            output_suffix='-random', index=None):
    """Keep count number of reads from BAM file."""
    sample_names = Parser.first(samples)
    if index is not None:
        sample_names = [sample_names[index]]
    for sample in sample_names:
        keeprandomreads_sample(sample, count, paired, threads, input_suffix, output_suffix)


def keeprandomreads_sample(sample, count=10000000, paired=True, threads=None, input_suffix='', output_suffix='-random'):
    """Keep count number of reads from BAM file for a single sample."""
    print('Keep {} of unpaired or paired reads from BAM file for sample {}'.format(count, sample))
    bam_input = sample + input_suffix + '.bam'
    sort_bam_o, sort_bam = tempfile.mkstemp(suffix='.bam')
    Bam.sort_by_readname(bam_input, sort_bam, threads)
    is_primary = (lambda r: (not r.is_secondary and not r.is_supplementary))
    count_read_callback = (lambda r: (r.is_read1 or not paired) and is_primary(r))
    with pysam.AlignmentFile(sort_bam, 'rb') as inbam:
        header = inbam.header
        in_count = inbam.count(until_eof=True, read_callback=count_read_callback)
    indexes = set(random.sample(range(0, in_count), min(count, in_count)))
    filter_bam_o, filter_bam = tempfile.mkstemp(suffix='.bam')
    with pysam.AlignmentFile(sort_bam, 'rb') as inbam, pysam.AlignmentFile(filter_bam, 'wb', header=header) as outbam:
        i = 0
        read_name = ""
        keep_read = False
        for aln in inbam.fetch(until_eof=True):
            if not is_primary(aln):
                continue
            if aln.is_paired and read_name == aln.query_name:
                # Process mate.
                if keep_read:
                    outbam.write(aln)
                continue
            read_name = aln.query_name
            keep_read = i in indexes
            if keep_read:
                outbam.write(aln)
            i = i + 1
    logging.debug(f"sample = {sample}, count = {count}, in_count = {in_count}, len indexes = {len(indexes)},"
                  f" max indexes = {max(indexes)}, i = {i}")
    output = sample + output_suffix + '.bam'
    Bam.sort(filter_bam, output, threads)


if __name__ == '__main__':
    keeprandomreadsbam()
