import filecmp
import logging
import multiprocessing
import os
from pathlib import Path
from shutil import copyfile
import subprocess
from unittest.mock import MagicMock, call, ANY, patch

import click
from click.testing import CliRunner, make_input_stream
from more_itertools.more import side_effect
import pytest

from robtools import Siqchip as sc


@pytest.fixture
def mock_testclass():
    siqchip_samples = sc.siqchip_samples
    siqchip_sample = sc.siqchip_sample
    prepare_parameters = sc.prepare_parameters
    run_siqchip = sc.run_siqchip
    run = subprocess.run
    yield
    sc.siqchip_samples = siqchip_samples
    sc.siqchip_sample = siqchip_sample
    sc.prepare_parameters = prepare_parameters
    sc.run_siqchip = run_siqchip
    subprocess.run = run
    

def siqchip_cmd_output(*args, **kwargs):
    folder = args[1][0][1]
    output = folder + '/chrchrI.ce'
    with open(output, 'w') as outfile:
        outfile.write('chrI\t10\t20\t0.1\n')
        outfile.write('chrI\t20\t30\t0.2\n')
    output = folder + '/chrchrII.ce'
    with open(output, 'w') as outfile:
        outfile.write('chrII\t10\t20\t0.1\n')
        outfile.write('chrII\t20\t30\t0.2\n')

    
def test_siqchip(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    sc.siqchip_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(sc.siqchip, ['--samples', samples])
    assert result.exit_code == 0
    sc.siqchip_samples.assert_called_once_with(samples, 'sacCer3.chrom.sizes', '-input-reads', '-reads', '-params', '-siqchip', 1, None)


def test_siqchip_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    chromosomes = 'human.chroms'
    input_suffix = '-myinput'
    ip_suffix = '-myip'
    params_suffix = '-params'
    output_suffix = '-myoutput'
    threads = 3
    index = 1
    sc.siqchip_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(sc.siqchip, ['--samples', samples, '--chromosomes', chromosomes, '--input-suffix', input_suffix, '--ip-suffix', ip_suffix, '--params-suffix', params_suffix, '--output-suffix', output_suffix, '--threads', threads, '--index', index])
    assert result.exit_code == 0
    sc.siqchip_samples.assert_called_once_with(samples, chromosomes, input_suffix, ip_suffix, params_suffix, output_suffix, threads, index)


def test_siqchip_samplesnotexists(testdir, mock_testclass):
    samples = 'samples.txt'
    sc.siqchip_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(sc.siqchip, ['--samples', samples])
    assert result.exit_code > 0
    sc.siqchip_samples.assert_not_called()


def test_siqchip_samples(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    sc.siqchip_sample = MagicMock()
    sc.siqchip_samples(samples)
    sc.siqchip_sample.assert_any_call('POLR2A', 'sacCer3.chrom.sizes', '-input-reads', '-reads', '-params', '-siqchip', 1)
    sc.siqchip_sample.assert_any_call('ASDURF', 'sacCer3.chrom.sizes', '-input-reads', '-reads', '-params', '-siqchip', 1)
    sc.siqchip_sample.assert_any_call('POLR1C', 'sacCer3.chrom.sizes', '-input-reads', '-reads', '-params', '-siqchip', 1)


def test_siqchip_samples_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    chromosomes = 'human.chroms'
    input_suffix = '-myinput'
    ip_suffix = '-myip'
    params_suffix = '-params'
    output_suffix = '-myoutput'
    threads = 3
    index = 1
    sc.siqchip_sample = MagicMock()
    sc.siqchip_samples(samples, chromosomes, input_suffix, ip_suffix, params_suffix, output_suffix, threads, index)
    sc.siqchip_sample.assert_called_once_with('ASDURF', chromosomes, input_suffix, ip_suffix, params_suffix, output_suffix, threads)

    
@patch('multiprocessing.Pool')
def test_siqchip_sample(mockpool, testdir, mock_testclass):
    sample = 'POLR2A'
    chromosomes = Path(__file__).parent.joinpath('sizes.txt')
    copyfile(chromosomes, 'sacCer3.chrom.sizes')
    input = sample + '-input-reads.bed'
    ip = sample + '-reads.bed'
    params = sample + '-params.in'
    output = sample + '-siqchip.bed'
    sc.prepare_parameters = MagicMock()
    mockpool_instance = mockpool().__enter__()
    mockpool_instance.starmap.side_effect = siqchip_cmd_output
    sc.siqchip_sample(sample)
    sc.prepare_parameters.assert_called_with(ANY, input, ip, params)
    folder = sc.prepare_parameters.call_args[0][0]
    mockpool.assert_any_call(processes=1)
    mockpool_instance.starmap.assert_any_call(sc.run_siqchip, [(['Slave.sh', 'chrI', input, ip], folder), (['Slave.sh', 'chrII', input, ip], folder)])
    os.path.isfile(output)
    with open(output, 'r') as outfile:
        assert 'chrI\t10\t20\t0.1\n' == outfile.readline()
        assert 'chrI\t20\t30\t0.2\n' == outfile.readline()
        assert 'chrII\t10\t20\t0.1\n' == outfile.readline()
        assert 'chrII\t20\t30\t0.2\n' == outfile.readline()


@patch('multiprocessing.Pool')
def test_siqchip_sample_parameters(mockpool, testdir, mock_testclass):
    sample = 'POLR2A'
    chromosomes = Path(__file__).parent.joinpath('sizes.txt')
    input_suffix = '-myinput'
    ip_suffix = '-myip'
    params_suffix = '-params'
    output_suffix = '-myoutput'
    threads = 3
    input = sample + input_suffix + '.bed'
    ip = sample + ip_suffix + '.bed'
    params = sample + params_suffix + '.in'
    output = sample + output_suffix + '.bed'
    sc.prepare_parameters = MagicMock()
    mockpool_instance = mockpool().__enter__()
    mockpool_instance.starmap.side_effect = siqchip_cmd_output
    sc.siqchip_sample(sample, chromosomes, input_suffix, ip_suffix, params_suffix, output_suffix, threads)
    sc.prepare_parameters.assert_called_with(ANY, input, ip, params)
    folder = sc.prepare_parameters.call_args[0][0]
    mockpool.assert_any_call(processes=threads)
    mockpool_instance.starmap.assert_any_call(sc.run_siqchip, [(['Slave.sh', 'chrI', input, ip], folder), (['Slave.sh', 'chrII', input, ip], folder)])
    os.path.isfile(output)
    with open(output, 'r') as outfile:
        assert 'chrI\t10\t20\t0.1\n' == outfile.readline()
        assert 'chrI\t20\t30\t0.2\n' == outfile.readline()
        assert 'chrII\t10\t20\t0.1\n' == outfile.readline()
        assert 'chrII\t20\t30\t0.2\n' == outfile.readline()


def test_prepare_parameters(testdir, mock_testclass):
    siqchip_folder = str(testdir) + '/siq-chip'
    os.mkdir(siqchip_folder)
    os.environ['SIQ_CHIP_BASE'] = str(siqchip_folder)
    folder = 'folder'
    os.mkdir(folder)
    sample = 'POLR2A'
    input = sample + '-input-reads.bed'
    copyfile(Path(__file__).parent.joinpath('sample2.bed'), input)
    ip = sample + '-reads.bed'
    copyfile(Path(__file__).parent.joinpath('sample.bed'), ip)
    siqchip_source = '2Dlow-mem.f'
    copyfile(Path(__file__).parent.joinpath('selection.txt'), siqchip_folder + '/' + siqchip_source)
    siqchip_exec = 'Slave.sh'
    copyfile(Path(__file__).parent.joinpath('intersect.txt'), siqchip_folder + '/' + siqchip_exec)
    params = sample + '-params.in'
    copyfile(Path(__file__).parent.joinpath('names.txt'), params)
    resi = 'resi'
    copyfile(Path(__file__).parent.joinpath('dataset.txt'), resi)
    sc.prepare_parameters(folder, input, ip, params)
    assert os.path.isfile(folder + '/' + input)
    filecmp.cmp(Path(__file__).parent.joinpath('sample2.bed'), folder + '/' + input)
    assert os.path.isfile(folder + '/' + ip)
    filecmp.cmp(Path(__file__).parent.joinpath('sample.bed'), folder + '/' + ip)
    assert os.path.isfile(folder + '/' + siqchip_source)
    filecmp.cmp(Path(__file__).parent.joinpath('selection.txt'), folder + '/' + siqchip_source)
    assert os.path.isfile(folder + '/' + siqchip_exec)
    filecmp.cmp(Path(__file__).parent.joinpath('intersect.txt'), folder + '/' + siqchip_exec)
    assert os.path.isfile(folder + '/params.in')
    filecmp.cmp(Path(__file__).parent.joinpath('names.txt'), folder + '/params.in')
    assert os.path.isfile(folder + '/' + resi)
    filecmp.cmp(Path(__file__).parent.joinpath('dataset.txt'), folder + '/' + resi)


def test_run_siqchip(testdir, mock_testclass):
    sample = 'POLR2A'
    input = sample + '-input-reads.bed'
    ip = sample + '-reads.bed'
    folder = 'folder'
    subprocess.run = MagicMock()
    sc.run_siqchip(['Slave.sh', 'chrI', input, ip], folder)
    subprocess.run.assert_any_call(['Slave.sh', 'chrI', input, ip], cwd=folder, check=True)
