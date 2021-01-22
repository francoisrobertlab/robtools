from distutils.command.check import check
import logging
import multiprocessing
import os
import re
from shutil import copyfile
import subprocess
import tempfile

import click

from robtools.bed import Bed
from robtools.txt import Parser


@click.command()
@click.option('--samples', type=click.Path(exists=True), default='samples.txt', show_default=True,
              help='Sample names listed one sample name by line.')
@click.option('--chromosomes', default='sacCer3.chrom.sizes', show_default=True,
              help='File containing chromosome names in the first column.')
@click.option('--input-suffix', default='-input-reads', show_default=True,
              help='Suffix to add to sample name to obtain input reads BED filename.')
@click.option('--ip-suffix', default='-reads', show_default=True,
              help='Suffix to add to sample name to obtain IP reads BED filename.')
@click.option('--params-suffix', default='-params', show_default=True,
              help='Suffix to add to sample name to obtain params filename (.in extension).')
@click.option('--output-suffix', default='-siqchip', show_default=True,
              help='Suffix added to sample name in output BED filename.')
@click.option('--threads', '-p', default=1, show_default=True,
              help='Number of threads used to process data per sample.')
@click.option('--index', type=int, default=None,
              help='Index of sample to process in samples file.')
def siqchip(samples, chromosomes, input_suffix, ip_suffix, params_suffix, output_suffix, threads, index):
    '''Runs siQ-ChIP for samples.'''
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    siqchip_samples(samples, chromosomes, input_suffix, ip_suffix, params_suffix, output_suffix, threads, index)


def siqchip_samples(samples, chromosomes='sacCer3.chrom.sizes', input_suffix='-input-reads', ip_suffix='-reads', params_suffix='-params', output_suffix='-siqchip', threads=1, index=None):
    '''Runs siQ-ChIP for samples.'''
    sample_names = Parser.first(samples)
    if index != None:
        sample_names = [sample_names[index]]
    for sample in sample_names:
        siqchip_sample(sample, chromosomes, input_suffix, ip_suffix, params_suffix, output_suffix, threads)


def siqchip_sample(sample, chromosomes='sacCer3.chrom.sizes', input_suffix='-input-reads', ip_suffix='-reads', params_suffix='-params', output_suffix='-siqchip', threads=1):
    '''Runs siQ-ChIP for sample.'''
    print ('Running siQ-ChIP for sample {}'.format(sample))
    input = sample + input_suffix + '.bed'
    ip = sample + ip_suffix + '.bed'
    ce_output = sample + output_suffix + '.ce'
    bed_output = sample + output_suffix + '.bed'
    track = 'track type=bedGraph name="' + sample + output_suffix + '"'
    bigwig = sample + output_suffix + '.bw'
    params = sample + params_suffix + '.in'
    chromosome_names = Parser.first(chromosomes)
    input_chromosomes = read_chromosomes(input, 2)
    ip_chromosomes = read_chromosomes(ip, 2)
    chromosome_names = [chromosome for chromosome in chromosome_names if chromosome in input_chromosomes and chromosome in ip_chromosomes]
    chromosome_pattern = re.compile('chr(.*)')
    cmds = [['Slave.sh', chromosome_pattern.match(chromosome).group(1), input, ip] for chromosome in chromosome_names]
    with tempfile.TemporaryDirectory() as folder:
        prepare_parameters(folder, input, ip, params)
        with multiprocessing.Pool(processes=threads) as pool:
            pool.starmap(run_siqchip, [(cmd, folder) for cmd in cmds])
        siqchip_outputs = [folder + '/' + chromosome + '.ce' for chromosome in chromosome_names]
        with open(ce_output, 'w') as wfd:
            for f in siqchip_outputs:
                with open(f, 'r') as fd:
                    for line in fd:
                        wfd.write('\t'.join(line.lstrip().split()))
                        wfd.write('\n')
        sort_output = folder + '/' + bed_output
        Bed.sort(ce_output, sort_output)
        with open(sort_output, 'r') as infile, open(bed_output, 'w') as outfile:
            outfile.write(track)
            outfile.write('\n')
            for line in infile:
                columns = line.rstrip('\n\r').split('\t')
                outfile.write(columns[0])
                outfile.write('\t')
                outfile.write(columns[1])
                outfile.write('\t')
                outfile.write(columns[2])
                outfile.write('\t')
                outfile.write(columns[3])
                outfile.write('\n')
        Bed.bedgraph_to_bigwig(bed_output, bigwig, chromosomes)


def read_chromosomes(bed, minimum_count=1):
    chromosomes = dict()
    with open(bed, 'r') as infile:
        for line in infile:
            if line.startswith('track') or line.startswith('browser') or line.startswith('#'):
                continue
            columns = line.rstrip('\r\n').split('\t')
            if not columns[0] in chromosomes:
                chromosomes[columns[0]] = 0
            chromosomes[columns[0]] = chromosomes[columns[0]] + 1
    return set([chromosome for chromosome in chromosomes if chromosomes[chromosome] >= minimum_count])

    
def prepare_parameters(folder, input, ip, params):
    siqchip_base = os.getenv('SIQ_CHIP_BASE', '')
    siqchip_source = (siqchip_base + '/' if siqchip_base else '') + '2Dlow-mem.f'
    siqchip_exec = (siqchip_base + '/' if siqchip_base else '') + 'Slave.sh'
    copyfile(siqchip_source, folder + '/2Dlow-mem.f')
    copyfile(siqchip_exec, folder + '/Slave.sh')
    copyfile(input, folder + '/' + input)
    copyfile(ip, folder + '/' + ip)
    copyfile(params, folder + '/params.in')
    copyfile('resi', folder + '/resi')
    
    
def run_siqchip(cmd, folder):
    logging.debug('Running {} in directory {}'.format(cmd, folder))
    subprocess.run(cmd, cwd=folder, check=True)


if __name__ == '__main__':
    siqchip()
