import logging
import os
import subprocess
import tempfile

import click

from robtools.bam import Bam
from robtools.txt import Parser


@click.command()
@click.option('--samples', '-s', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--paired/--unpaired', '-p/-u', default=True, show_default=True,
              help='Sample reads are paired')
@click.option('--dedup/--no-dedup', '-d/-nd', default=True, show_default=True,
              help='Remove duplicates')
@click.option('--quality', '-q', type=int, default=None, show_default=True,
              help='Only include reads with mapping quality >= INT [0]')
@click.option('--threads', '-t', default=1, show_default=True,
              help='Number of threads used to process data per sample.')
@click.option('--input-suffix', '-is', default='', show_default=True,
              help='Suffix added to sample name in BAM filename for input.')
@click.option('--output-suffix', '-os', default='', show_default=True,
              help='Suffix added to sample name in BAM filename for output.')
@click.option('--index', '-i', type=int, default=None,
              help='Index of sample to process in samples file.')
def filterbam(samples, paired, dedup, quality, threads, input_suffix, output_suffix, index):
    '''Filter BAM file to keep only properly paired reads and remove supplementary alignments and duplicates.'''
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    filter_bam(samples, paired, dedup, quality, threads, input_suffix, output_suffix, index)


def filter_bam(samples='samples.txt', paired=True, dedup=True, quality=None, threads=None, input_suffix='',
               output_suffix='', index=None):
    '''Filter BAM file to keep only properly paired reads and remove supplementary alignments and duplicates.'''
    sample_names = Parser.first(samples)
    if index != None:
        sample_names = [sample_names[index]]
    for sample in sample_names:
        filter_bam_sample(sample, paired, dedup, quality, threads, input_suffix, output_suffix)


def filter_bam_sample(sample, paired, dedup, quality=None, threads=None, input_suffix='', output_suffix=''):
    '''Filter BAM file to keep only properly paired reads and remove supplementary alignments and duplicates.'''
    print('Filtering BAM for sample {}'.format(sample))
    bam = sample + input_suffix + '.bam'
    bam_filtered = sample + output_suffix + '-filtered.bam'
    filter_mapped(bam, bam_filtered, paired, quality, threads)
    if dedup:
        bam_dedup = sample + output_suffix + '-dedup.bam'
        remove_duplicates(bam_filtered, bam_dedup, threads)


def filter_mapped(bam_input, bam_output, paired, quality=None, threads=None):
    '''Filter BAM file to remove poorly mapped sequences.'''
    print('Filtering BAM {} to remove poorly mapped sequences'.format(bam_input))
    temp_o, temp = tempfile.mkstemp(suffix='.bam')
    cmd = ['samtools', 'view', '-b', '-F', '2048', '-F', '256']
    if bool(paired):
        cmd.extend(['-f', '2'])
    else:
        cmd.extend(['-F', '4'])
    if quality:
        cmd.extend(['-q', str(quality)])
    if not threads is None and threads > 1:
        cmd.extend(['--threads', str(threads - 1)])
    cmd.extend(['-o', temp, bam_input])
    logging.debug('Running {}'.format(cmd))
    subprocess.run(cmd, check=True)
    Bam.sort(temp, bam_output, threads)
    os.remove(temp)


def remove_duplicates(bam_input, bam_output, threads=None):
    '''Remove duplicated sequences from BAM file.'''
    print('Removing duplicated sequences from BAM {}'.format(bam_input))
    sort_bam_o, sort_bam = tempfile.mkstemp(suffix='.bam')
    Bam.sort_by_readname(bam_input, sort_bam, threads)
    fixmate_o, fixmate = tempfile.mkstemp(suffix='.bam')
    cmd = ['samtools', 'fixmate', '-m']
    if not threads is None and threads > 1:
        cmd.extend(['--threads', str(threads - 1)])
    cmd.extend([sort_bam, fixmate])
    logging.debug('Running {}'.format(cmd))
    subprocess.run(cmd, check=True)
    os.remove(sort_bam)
    sort_fix_o, sort_fix = tempfile.mkstemp(suffix='.bam')
    Bam.sort(fixmate, sort_fix, threads)
    os.remove(fixmate)
    markdup_o, markdup = tempfile.mkstemp(suffix='.bam')
    cmd = ['samtools', 'markdup', '-r']
    if not threads is None and threads > 1:
        cmd.extend(['--threads', str(threads - 1)])
    cmd.extend([sort_fix, markdup])
    logging.debug('Running {}'.format(cmd))
    subprocess.run(cmd, check=True)
    os.remove(sort_fix)
    Bam.sort(markdup, bam_output, threads)
    os.remove(markdup)


if __name__ == '__main__':
    filterbam()
