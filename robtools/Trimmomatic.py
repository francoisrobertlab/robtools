import logging
import os
import subprocess

import click

from robtools.seq import Fastq
from robtools.txt import Parser

TRIMMOMATIC_JAR_ENV = 'TRIMMOMATIC_JAR'
TRIMMOMATIC_ADAPTERS_ENV = 'TRIMMOMATIC_ADAPTERS'
SBATCH_JAVA_MEM_ENV = 'SLURM_MEM_PER_NODE'


@click.command(context_settings=dict(
    ignore_unknown_options=True,
))
@click.option('--samples', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--input-suffix', '-is', default='', show_default=True,
              help='Suffix added to sample name in FASTQ filename for input.')
@click.option('--output-suffix', '-os', default='-trim', show_default=True,
              help='Suffix added to sample name for FASTQ output - single-ended data only.')
@click.option('--paired-suffix', '-ps', default='-paired', show_default=True,
              help='Suffix added to sample name for paired FASTQ output - paired-end data only.')
@click.option('--unpaired-suffix', '-us', default='-unpaired', show_default=True,
              help='Suffix added to sample name for paired FASTQ output - paired-end data only.')
@click.option('--trimmers', default=None,
              help='Trimmers to use. ex: "LEADING:3 TRAILING:3"')
@click.option('--index', type=int, default=None,
              help='Index of sample to process in samples file.')
@click.argument('trim_args', nargs=-1, type=click.UNPROCESSED)
def trimmomatic(samples, input_suffix, output_suffix, paired_suffix, unpaired_suffix, trimmers, index, trim_args):
    '''Trim FASTQ sample files using trimmomatic program.'''
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    trimmomatic_samples(samples, input_suffix, output_suffix, paired_suffix, unpaired_suffix, trimmers, index,
                        trim_args)


def trimmomatic_samples(samples='samples.txt', input_suffix='', output_suffix='-trim', paired_suffix='-paired',
                        unpaired_suffix='-unpaired', trimmers=None, index=None, trim_args=()):
    '''Trim FASTQ sample files using trimmomatic program.'''
    sample_names = Parser.first(samples)
    if index != None:
        sample_names = [sample_names[index]]
    for sample in sample_names:
        trimmomatic_sample(sample, input_suffix, output_suffix, paired_suffix, unpaired_suffix, trimmers, trim_args)


def trimmomatic_sample(sample, input_suffix='', output_suffix='-trim', paired_suffix='-paired',
                       unpaired_suffix='-unpaired', trimmers=None, trim_args=()):
    '''Trim FASTQ of one sample files using trimmomatic program.'''
    print('Trim FASTQ files of sample {}'.format(sample))
    fastq1 = Fastq.fastq(sample + input_suffix, 1)
    if fastq1 is None:
        raise AssertionError('Cannot find FASTQ files for sample ' + sample + input_suffix)
    suffix1 = fastq1[len(sample) + len(input_suffix): len(fastq1)]
    fastq2 = Fastq.fastq(sample + input_suffix, 2)
    if trimmers:
        trimmers = trimmers.split()
        trimmers = fix_adapters(trimmers)
    if fastq2 is not None and os.path.isfile(fastq2):
        fastq1_paired = sample + paired_suffix + suffix1
        fastq1_unpaired = sample + unpaired_suffix + suffix1
        suffix2 = fastq2[len(sample) + len(input_suffix): len(fastq2)]
        fastq2_paired = sample + paired_suffix + suffix2 if fastq2 is not None else ''
        fastq2_unpaired = sample + unpaired_suffix + suffix2 if fastq2 is not None else ''
        trimmomatic_paired(fastq1, fastq1_paired, fastq1_unpaired, fastq2, fastq2_paired, fastq2_unpaired, trimmers,
                           trim_args)
    else:
        output = sample + output_suffix + suffix1
        trimmomatic_single(fastq1, output, trimmers, trim_args)


def fix_adapters(trimmers):
    adapters_dir = os.getenv(TRIMMOMATIC_ADAPTERS_ENV, '')
    fixed = []
    for trimmer in trimmers:
        if trimmer.startswith('ILLUMINACLIP:'):
            parts = trimmer.split(':')
            file = parts[1]
            if not os.path.exists(file):
                file = adapters_dir + '/' + file
                if os.path.exists(file):
                    parts[1] = file
            trimmer = ':'.join(parts)
        fixed.append(trimmer)
    return fixed


def trimmomatic_single(fastq, output, trimmers, trim_args=()):
    '''Run trimmomatic on single FASTQ file.'''
    trimmomatic_jar = os.getenv(TRIMMOMATIC_JAR_ENV, 'trimmomatic.jar')
    mem = os.getenv(SBATCH_JAVA_MEM_ENV, None)
    cmd = ['java']
    if mem:
        cmd.extend(['-Xmx' + mem])
    cmd.extend(['-jar', trimmomatic_jar, 'SE'] + list(trim_args))
    cmd.extend([fastq, output])
    if trimmers:
        cmd.extend(trimmers)
    logging.debug('Running {}'.format(cmd))
    subprocess.run(cmd, check=True)


def trimmomatic_paired(fastq1, fastq1_paired, fastq1_unpaired, fastq2, fastq2_paired, fastq2_unpaired, trimmers,
                       trim_args=()):
    '''Run trimmomatic on paired FASTQ files.'''
    trimmomatic_jar = os.getenv(TRIMMOMATIC_JAR_ENV, 'trimmomatic.jar')
    mem = os.getenv(SBATCH_JAVA_MEM_ENV, None)
    cmd = ['java']
    if mem:
        cmd.extend(['-Xmx' + mem])
    cmd.extend(['-jar', trimmomatic_jar, 'PE'] + list(trim_args))
    cmd.extend([fastq1, fastq2, fastq1_paired, fastq1_unpaired, fastq2_paired, fastq2_unpaired])
    if trimmers:
        cmd.extend(trimmers)
    logging.debug('Running {}'.format(cmd))
    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    trimmomatic()
