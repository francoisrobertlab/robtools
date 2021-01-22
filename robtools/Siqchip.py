from distutils.command.check import check
import logging
import multiprocessing
import os
import re
from shutil import copyfile
import shutil
import subprocess
import tempfile

import click

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
    output = sample + output_suffix + '.bed'
    params = sample + params_suffix + '.in'
    chromosome_names = Parser.first(chromosomes)
    chromosome_pattern = re.compile('chr(.*)')
    cmds = [['Slave.sh', chromosome_pattern.match(chromosome).group(1), input, ip] for chromosome in chromosome_names]
    with tempfile.TemporaryDirectory() as folder:
        prepare_parameters(folder, input, ip, params)
        with multiprocessing.Pool(processes=threads) as pool:
            pool.starmap(run_siqchip, [(cmd, folder) for cmd in cmds])
        siqchip_outputs = [folder + '/' + chromosome + '.ce' for chromosome in chromosome_names]
        with open(output, 'wb') as wfd:
            for f in siqchip_outputs:
                with open(f, 'rb') as fd:
                    shutil.copyfileobj(fd, wfd)


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
