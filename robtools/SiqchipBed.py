from distutils.command.check import check
import logging
import subprocess
import tempfile

import click

from robtools.bed import Bed
from robtools.txt import Parser


@click.command()
@click.option('--samples', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--input-suffix', default='-dedup', show_default=True,
              help='Suffix to add to sample name to obtain input reads BED filename.')
@click.option('--output-suffix', default='-reads', show_default=True,
              help='Suffix added to sample name in output BED filename.')
@click.option('--index', type=int, default=None,
              help='Index of sample to process in samples file.')
def siqchipbed(samples, input_suffix, output_suffix, index):
    '''Convert BAM to BED for use with siQ-ChIP.'''
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    siqchipbed_samples(samples, input_suffix, output_suffix, index)


def siqchipbed_samples(samples, input_suffix='-dedup', output_suffix='-reads', index=None):
    '''Convert BAM to BED for use with siQ-ChIP.'''
    sample_names = Parser.first(samples)
    if index != None:
        sample_names = [sample_names[index]]
    for sample in sample_names:
        siqchipbed_sample(sample, input_suffix, output_suffix)


def siqchipbed_sample(sample, input_suffix='-dedup', output_suffix='-reads'):
    '''Convert BAM to BED for use with siQ-ChIP for a single sample.'''
    print ('Converting BAM to BED for siQ-ChIP for sample {}'.format(sample))
    input = sample + input_suffix + '.bam'
    output = sample + output_suffix + '.bed'
    with tempfile.NamedTemporaryFile(mode='w+t') as sam:
        cmd = ['samtools', 'view', '-o', sam.name, input]
        logging.debug('Running {}'.format(cmd))
        subprocess.run(cmd, check=True)
        sam.seek(0)
        with tempfile.NamedTemporaryFile(mode='w+t') as bed:
            for line in sam:
                columns = line.rstrip('\r\n').split('\t')
                flags = int(columns[1])
                if flags == 99 or flags == 163:
                    start = int(columns[3])
                    length = int(columns[8]) - 1
                    end = start + length
                    bed.write(columns[2])
                    bed.write('\t')
                    bed.write(str(start))
                    bed.write('\t')
                    bed.write(str(end))
                    bed.write('\t')
                    bed.write(str(length))
                    bed.write('\n')
            bed.seek(0)
            Bed.sort(bed.name, output)


if __name__ == '__main__':
    siqchipbed()
