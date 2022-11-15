import gzip
import logging
import random
import re

import click

from robtools.txt import Parser


@click.command()
@click.option('--samples', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--count', type=int, default=10000000, show_default=True, help='Number of reads to keep.')
@click.option('--paired/--unpaired', '-p/-u', default=True, show_default=True, help='Sample reads are paired')
@click.option('--input-suffix', default='', show_default=True,
              help='Suffix to add to sample name to obtain input reads FASTQ filename.')
@click.option('--output-suffix', default='-random', show_default=True,
              help='Suffix added to sample name in output FASTQ filename.')
@click.option('--index', type=int, default=None, help='Index of sample to process in samples file.')
def keeprandomreads(samples, count, paired, input_suffix, output_suffix, index):
    """Keep count number of reads from FASTQ files."""
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    keeprandomreads_samples(samples, count, paired, input_suffix, output_suffix, index)


def keeprandomreads_samples(samples, count=10000000, paired=True, input_suffix='', output_suffix='-random', index=None):
    """Keep count number of reads from FASTQ files."""
    sample_names = Parser.first(samples)
    if index is not None:
        sample_names = [sample_names[index]]
    for sample in sample_names:
        keeprandomreads_sample(sample, count, paired, input_suffix, output_suffix)


def keeprandomreads_sample(sample, count=10000000, paired=True, input_suffix='', output_suffix='-random'):
    """Keep count number of reads from FASTQ files for a single sample."""
    print('Keep {} of unpaired or paired reads from FASTQ files for sample {}'.format(count, sample))
    fastq1 = sample + input_suffix + '_R1.fastq.gz'
    fastq2 = sample + input_suffix + '_R2.fastq.gz'
    in_count = 0
    with gzip.open(fastq1, 'rt') as fastq1_in:
        for line in fastq1_in:
            if line.startswith('@'):
                in_count = in_count + 1
    indexes = set(random.sample(range(0, in_count), min(count, in_count)))
    output1 = sample + output_suffix + '_R1.fastq.gz'
    output2 = sample + output_suffix + '_R2.fastq.gz'
    in_count = -1
    if paired:
        with gzip.open(fastq1, 'rt') as fastq1_in, gzip.open(output1, 'wt') as output1_out:
            with gzip.open(fastq2, 'rt') as fastq2_in, gzip.open(output2, 'wt') as output2_out:
                for line1 in fastq1_in:
                    line2 = fastq2_in.readline()
                    if line1.startswith('@'):
                        in_count = in_count + 1
                        read_name1 = re.split('\\s', line1)[0]
                        read_name2 = re.split('\\s', line2)[0]
                        assert line2.startswith(
                            '@'), f"Format of FASTQ file {fastq2} does not seem right at read {read_name2}"
                        assert read_name1 == read_name2, f"Read {read_name1} from file {fastq1} does not match read " \
                                                         f"{read_name2} from file {fastq2}"
                    if in_count in indexes:
                        output1_out.write(line1)
                        output2_out.write(line2)
    else:
        with gzip.open(fastq1, 'rt') as fastq1_in, gzip.open(output1, 'wt') as output1_out:
            for line1 in fastq1_in:
                if line1.startswith('@'):
                    in_count = in_count + 1
                if in_count in indexes:
                    output1_out.write(line1)


if __name__ == '__main__':
    keeprandomreads()
