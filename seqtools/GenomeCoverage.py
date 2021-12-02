from distutils.command.check import check
import logging
import os
import subprocess
import tempfile

import click

from seqtools import Split
from seqtools.bed import Bed
from seqtools.txt import Parser

BASE_SCALE = 1000000


def validate_output_suffix(ctx, param, value):
    '''Validates that output suffix is different than input suffix'''
    input_suffix = ctx.params['input_suffix'] if 'input_suffix' in ctx.params else ''
    if value == input_suffix:
        raise click.BadParameter('output suffix "{}" must be different than input suffix'.format(value))
    else:
        return value


def validate_spike_suffix(ctx, param, value):
    '''Validates that scale and spike suffix are not both specified'''
    scale = ctx.params['scale'] if 'scale' in ctx.params else None
    if value and scale:
        raise click.BadParameter('--spike-suffix cannot be used if --scale is present')
    else:
        return value


def validate_control_suffix(ctx, param, value):
    '''Validates that spike suffix and spike control suffix is also specified'''
    spike_suffix = ctx.params['spike_suffix'] if 'spike_suffix' in ctx.params else None
    if value and not spike_suffix:
        raise click.BadParameter('--control-suffix requires --spike-suffix and --spike-control-suffix')
    else:
        return value


def validate_spike_control_suffix(ctx, param, value):
    '''Validates that spike suffix and control suffix is also specified'''
    spike_suffix = ctx.params['spike_suffix'] if 'spike_suffix' in ctx.params else None
    control_suffix = ctx.params['control_suffix'] if 'control_suffix' in ctx.params else None
    if value and (not spike_suffix or not control_suffix):
        raise click.BadParameter('--spike-control-suffix requires --spike-suffix and --control-suffix')
    elif not value and control_suffix and spike_suffix:
        raise click.BadParameter('--control-suffix requires --spike-suffix and --spike-control-suffix')
    else:
        return value


@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('--samples', '-s', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--sizes', '-S', type=click.Path(exists=True), default='sacCer3.chrom.sizes', show_default=True,
              help='Size of chromosomes.')
@click.option('--scale', '-C', type=float, default=None,
              help='Scale for genome coverage. Defaults to 1000000 / number of reads.')
@click.option('--strand', '-T', type=click.Choice(['+', '-']), default=None, show_default=True,
              help='Calculate coverage of intervals from a specific strand.')
@click.option('--input-suffix', '-is', default='', show_default=True,
              help='Suffix added to sample name in BED filename for input.')
@click.option('--output-suffix', '-os', callback=validate_output_suffix, default='-cov', show_default=True,
              help='Suffix added to sample name in BED filename for output.')
@click.option('--spike-suffix', callback=validate_spike_suffix, default=None,
              help='Suffix added to sample name of BED file containing spiked reads.')
@click.option('--control-suffix', callback=validate_control_suffix, default=None,
              help='Suffix added to sample name of BED file containing control(input) reads.')
@click.option('--spike-control-suffix', callback=validate_spike_control_suffix, default=None,
              help='Suffix added to sample name of BED file containing control(input) spiked reads.')
@click.option('--index', '-i', type=int, default=None,
              help='Index of sample to process in samples file.')
@click.argument('genomecov_args', nargs=-1, type=click.UNPROCESSED)
def genomecov(samples, sizes, scale, strand, input_suffix, output_suffix, spike_suffix, control_suffix, spike_control_suffix, index, genomecov_args):
    '''
    Compute genome coverage on samples.

    \b
    - Scaling parameter:
        \b
        - If --spike-suffix is not present, scaling becomes
          1000000 / reads.
        - If --spike-suffix is present, scaling becomes
          1000000 / spiked reads.
        - If --spike-suffix, --control-suffix and --spike-control-suffix are present, scaling becomes
          1000000 * control spiked reads / (spiked reads * control reads).
    '''
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    genome_coverage_samples(samples, sizes, scale, strand, input_suffix, output_suffix, spike_suffix, control_suffix, spike_control_suffix, index, genomecov_args)


def genome_coverage_samples(samples='samples.txt', sizes='sacCer3.chrom.sizes', scale=None, strand=None, input_suffix='', output_suffix='-cov', spike_suffix=None, control_suffix=None, spike_control_suffix=None, index=None, genomecov_args=()):
    '''Compute genome coverage on samples.'''
    sample_names = Parser.first(samples)
    if index != None:
        sample_names = [sample_names[index]]
    for sample in sample_names:
        sample_splits_genome_coverage(sample, sizes, scale, strand, input_suffix, output_suffix, spike_suffix, control_suffix, spike_control_suffix, genomecov_args)


def sample_splits_genome_coverage(sample, sizes, scale=None, strand=None, input_suffix='', output_suffix='-cov', spike_suffix=None, control_suffix=None, spike_control_suffix=None, genomecov_args=()):
    '''Compute genome coverage on a single sample.'''
    print ('Computing genome coverage on sample {}'.format(sample))
    genome_coverage(sample, sizes, scale, strand, input_suffix, output_suffix, spike_suffix, control_suffix, spike_control_suffix, genomecov_args)
    splits = Split.splits(sample)
    for split in splits:
        genome_coverage(split, sizes, scale, strand, input_suffix, output_suffix, spike_suffix, control_suffix, spike_control_suffix, genomecov_args)


def genome_coverage(sample, sizes, scale=None, strand=None, input_suffix='', output_suffix='-cov', spike_suffix=None, control_suffix=None, spike_control_suffix=None, genomecov_args=()):
    bed_source = sample + input_suffix + '.bed'
    if not scale:
        if spike_suffix:
            spiked_count = Bed.count_bed(sample + spike_suffix + '.bed')
            scale = BASE_SCALE / max(spiked_count, 1)
            if control_suffix and spike_control_suffix:
                control_count = Bed.count_bed(sample + control_suffix + '.bed')
                spike_control_count = Bed.count_bed(sample + spike_control_suffix + '.bed')
                scale = scale * spike_control_count / max(control_count, 1)
        else:
            count = Bed.count_bed(bed_source)
            scale = BASE_SCALE / max(count, 1)
    print('Computing genome coverage on BED {} with scale {}'.format(bed_source, scale))
    bed = sample + output_suffix + '.bed'
    bigwig = sample + output_suffix + '.bw'
    if strand:
        bed = sample + output_suffix + ('-neg' if strand == '-' else '-pos') + '.bed'
        bigwig = sample + output_suffix + ('-neg' if strand == '-' else '-pos') + '.bw'
    coverage(bed_source, bed, sizes, sample, scale, strand, genomecov_args)
    Bed.bedgraph_to_bigwig(bed, bigwig, sizes)


def coverage(bed_input, bed_output, sizes, sample, scale=None, strand=None, genomecov_args=()):
    '''Compute genome coverage.'''
    coverage_output_o, coverage_output = tempfile.mkstemp(suffix='.bed')
    cmd = ['bedtools', 'genomecov', '-bg', '-i', bed_input, '-g', sizes] + list(genomecov_args)
    if scale:
        cmd.extend(['-scale', str(scale)])
    if strand:
        cmd.extend(['-strand', strand])
    logging.debug('Running {}'.format(cmd))
    with open(coverage_output_o, 'w') as outfile:
        subprocess.run(cmd, stdout=outfile, check=True)
    sort_output_o, sort_output = tempfile.mkstemp(suffix='.bed')
    Bed.sort(coverage_output, sort_output)
    os.remove(coverage_output)
    track = 'track type=bedGraph name="' + sample
    if strand:
        track += ' Minus' if strand == '-' else ' Plus'
    track += '"'
    with open(sort_output_o, 'r') as infile, open(bed_output, 'w') as outfile:
        outfile.write(track + '\n')
        outfile.writelines(infile)
    os.remove(sort_output)


if __name__ == '__main__':
    genomecov()