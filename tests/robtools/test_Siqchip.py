import filecmp
import logging
import multiprocessing
import os
from pathlib import Path
from shutil import copyfile
import subprocess
from unittest.mock import MagicMock, call, ANY, patch

from attr.validators import instance_of
import click
from click.testing import CliRunner, make_input_stream
from more_itertools.more import side_effect
import pytest

from robtools import Siqchip as sc
from robtools.bed import Bed


@pytest.fixture
def mock_testclass():
    siqchip_samples = sc.siqchip_samples
    siqchip_sample = sc.siqchip_sample
    prepare_parameters = sc.prepare_parameters
    run_siqchip = sc.run_siqchip
    read_chromosomes = sc.read_chromosomes
    sort = Bed.sort
    bedgraph_to_bigwig = Bed.bedgraph_to_bigwig
    run = subprocess.run
    yield
    sc.siqchip_samples = siqchip_samples
    sc.siqchip_sample = siqchip_sample
    sc.prepare_parameters = prepare_parameters
    sc.run_siqchip = run_siqchip
    sc.read_chromosomes = read_chromosomes
    Bed.sort = sort
    Bed.bedgraph_to_bigwig = bedgraph_to_bigwig
    subprocess.run = run
    

def siqchip_cmd_output(*args, **kwargs):
    folder = args[1][0][1]
    output = folder + '/chrI.ce'
    with open(output, 'w') as outfile:
        outfile.write(' cI  10  20  0.1  0.11\n')
        outfile.write(' cI  20  30  0.2  0.19\n')
    output = folder + '/chrII.ce'
    with open(output, 'w') as outfile:
        outfile.write(' chrII  10  20  0.1  0.09\n')
        outfile.write(' chrII   20 30   0.2 0.21\n')

    
def temp2file(*args, **kwargs):
    input = args[0]
    output = args[1]
    copyfile(input, output)


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
    sizes = Path(__file__).parent.joinpath('sizes.txt')
    chromosomes = 'sacCer3.chrom.sizes'
    copyfile(sizes, chromosomes)
    input = sample + '-input-reads.bed'
    ip = sample + '-reads.bed'
    params = sample + '-params.in'
    ce_output = sample + '-siqchip.ce'
    bed_output = sample + '-siqchip.bed'
    bigwig = sample + '-siqchip.bw'
    sc.prepare_parameters = MagicMock()
    sc.read_chromosomes = MagicMock(return_value=['chrI', 'chrII'])
    Bed.sort = MagicMock(side_effect=temp2file)
    Bed.bedgraph_to_bigwig = MagicMock()
    mockpool_instance = mockpool().__enter__()
    mockpool_instance.starmap.side_effect = siqchip_cmd_output
    sc.siqchip_sample(sample)
    sc.prepare_parameters.assert_called_with(ANY, input, ip, params)
    folder = sc.prepare_parameters.call_args[0][0]
    sc.read_chromosomes.assert_any_call(input, 2)
    sc.read_chromosomes.assert_any_call(ip, 2)
    mockpool.assert_any_call(processes=1)
    mockpool_instance.starmap.assert_any_call(sc.run_siqchip, [(['Slave.sh', 'I', input, ip], folder), (['Slave.sh', 'II', input, ip], folder)])
    Bed.sort.assert_called_with(ANY, ANY)
    assert isinstance(Bed.sort.call_args[0][0], str)
    assert isinstance(Bed.sort.call_args[0][1], str)
    Bed.bedgraph_to_bigwig.assert_called_with(bed_output, bigwig, chromosomes)
    os.path.isfile(ce_output)
    with open(ce_output, 'r') as outfile:
        assert 'chrI\t10\t20\t0.1\t0.11\n' == outfile.readline()
        assert 'chrI\t20\t30\t0.2\t0.19\n' == outfile.readline()
        assert 'chrII\t10\t20\t0.1\t0.09\n' == outfile.readline()
        assert 'chrII\t20\t30\t0.2\t0.21\n' == outfile.readline()
    os.path.isfile(bed_output)
    with open(bed_output, 'r') as outfile:
        assert 'track type=bedGraph name="' + sample + '-siqchip"\n' == outfile.readline()
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
    ce_output = sample + output_suffix + '.ce'
    bed_output = sample + output_suffix + '.bed'
    bigwig = sample + output_suffix + '.bw'
    sc.prepare_parameters = MagicMock()
    sc.read_chromosomes = MagicMock(return_value=['chrI', 'chrII'])
    Bed.sort = MagicMock(side_effect=temp2file)
    Bed.bedgraph_to_bigwig = MagicMock()
    mockpool_instance = mockpool().__enter__()
    mockpool_instance.starmap.side_effect = siqchip_cmd_output
    sc.siqchip_sample(sample, chromosomes, input_suffix, ip_suffix, params_suffix, output_suffix, threads)
    sc.prepare_parameters.assert_called_with(ANY, input, ip, params)
    folder = sc.prepare_parameters.call_args[0][0]
    sc.read_chromosomes.assert_any_call(input, 2)
    sc.read_chromosomes.assert_any_call(ip, 2)
    mockpool.assert_any_call(processes=threads)
    mockpool_instance.starmap.assert_any_call(sc.run_siqchip, [(['Slave.sh', 'I', input, ip], folder), (['Slave.sh', 'II', input, ip], folder)])
    Bed.sort.assert_called_with(ANY, ANY)
    assert isinstance(Bed.sort.call_args[0][0], str)
    assert isinstance(Bed.sort.call_args[0][1], str)
    Bed.bedgraph_to_bigwig.assert_called_with(bed_output, bigwig, chromosomes)
    os.path.isfile(ce_output)
    with open(ce_output, 'r') as outfile:
        assert 'chrI\t10\t20\t0.1\t0.11\n' == outfile.readline()
        assert 'chrI\t20\t30\t0.2\t0.19\n' == outfile.readline()
        assert 'chrII\t10\t20\t0.1\t0.09\n' == outfile.readline()
        assert 'chrII\t20\t30\t0.2\t0.21\n' == outfile.readline()
    os.path.isfile(bed_output)
    with open(bed_output, 'r') as outfile:
        assert 'track type=bedGraph name="' + sample + output_suffix + '"\n' == outfile.readline()
        assert 'chrI\t10\t20\t0.1\n' == outfile.readline()
        assert 'chrI\t20\t30\t0.2\n' == outfile.readline()
        assert 'chrII\t10\t20\t0.1\n' == outfile.readline()
        assert 'chrII\t20\t30\t0.2\n' == outfile.readline()


@patch('multiprocessing.Pool')
def test_siqchip_sample_missingchromosomeinput(mockpool, testdir, mock_testclass):
    sample = 'POLR2A'
    sizes = Path(__file__).parent.joinpath('sizes.txt')
    chromosomes = 'sacCer3.chrom.sizes'
    copyfile(sizes, chromosomes)
    input = sample + '-input-reads.bed'
    ip = sample + '-reads.bed'
    params = sample + '-params.in'
    ce_output = sample + '-siqchip.ce'
    bed_output = sample + '-siqchip.bed'
    bigwig = sample + '-siqchip.bw'
    sc.prepare_parameters = MagicMock()
    sc.read_chromosomes = MagicMock(side_effect=[['chrII'], ['chrI', 'chrII']])
    Bed.sort = MagicMock(side_effect=temp2file)
    Bed.bedgraph_to_bigwig = MagicMock()
    mockpool_instance = mockpool().__enter__()
    mockpool_instance.starmap.side_effect = siqchip_cmd_output
    sc.siqchip_sample(sample)
    sc.prepare_parameters.assert_called_with(ANY, input, ip, params)
    folder = sc.prepare_parameters.call_args[0][0]
    sc.read_chromosomes.assert_any_call(input, 2)
    sc.read_chromosomes.assert_any_call(ip, 2)
    mockpool.assert_any_call(processes=1)
    mockpool_instance.starmap.assert_any_call(sc.run_siqchip, [(['Slave.sh', 'II', input, ip], folder)])
    Bed.sort.assert_called_with(ANY, ANY)
    assert isinstance(Bed.sort.call_args[0][0], str)
    Bed.bedgraph_to_bigwig.assert_called_with(bed_output, bigwig, chromosomes)
    os.path.isfile(ce_output)
    with open(ce_output, 'r') as outfile:
        assert 'chrII\t10\t20\t0.1\t0.09\n' == outfile.readline()
        assert 'chrII\t20\t30\t0.2\t0.21\n' == outfile.readline()
    os.path.isfile(bed_output)
    with open(bed_output, 'r') as outfile:
        assert 'track type=bedGraph name="' + sample + '-siqchip"\n' == outfile.readline()
        assert 'chrII\t10\t20\t0.1\n' == outfile.readline()
        assert 'chrII\t20\t30\t0.2\n' == outfile.readline()


@patch('multiprocessing.Pool')
def test_siqchip_sample_missingchromosomeip(mockpool, testdir, mock_testclass):
    sample = 'POLR2A'
    sizes = Path(__file__).parent.joinpath('sizes.txt')
    chromosomes = 'sacCer3.chrom.sizes'
    copyfile(sizes, chromosomes)
    input = sample + '-input-reads.bed'
    ip = sample + '-reads.bed'
    params = sample + '-params.in'
    ce_output = sample + '-siqchip.ce'
    bed_output = sample + '-siqchip.bed'
    bigwig = sample + '-siqchip.bw'
    sc.prepare_parameters = MagicMock()
    sc.read_chromosomes = MagicMock(side_effect=[['chrI', 'chrII'], ['chrII']])
    Bed.sort = MagicMock(side_effect=temp2file)
    Bed.bedgraph_to_bigwig = MagicMock()
    mockpool_instance = mockpool().__enter__()
    mockpool_instance.starmap.side_effect = siqchip_cmd_output
    sc.siqchip_sample(sample)
    sc.prepare_parameters.assert_called_with(ANY, input, ip, params)
    folder = sc.prepare_parameters.call_args[0][0]
    mockpool.assert_any_call(processes=1)
    mockpool_instance.starmap.assert_any_call(sc.run_siqchip, [(['Slave.sh', 'II', input, ip], folder)])
    Bed.sort.assert_called_with(ANY, ANY)
    assert isinstance(Bed.sort.call_args[0][0], str)
    Bed.bedgraph_to_bigwig.assert_called_with(bed_output, bigwig, chromosomes)
    os.path.isfile(ce_output)
    with open(ce_output, 'r') as outfile:
        assert 'chrII\t10\t20\t0.1\t0.09\n' == outfile.readline()
        assert 'chrII\t20\t30\t0.2\t0.21\n' == outfile.readline()
    os.path.isfile(bed_output)
    with open(bed_output, 'r') as outfile:
        assert 'track type=bedGraph name="' + sample + '-siqchip"\n' == outfile.readline()
        assert 'chrII\t10\t20\t0.1\n' == outfile.readline()
        assert 'chrII\t20\t30\t0.2\n' == outfile.readline()


def test_read_chromosomes(testdir, mock_testclass):
    bed = Path(__file__).parent.joinpath('siqchip-reads.bed')
    chromosomes = sc.read_chromosomes(bed)
    assert 2 == len(chromosomes)
    assert 'chr1' in chromosomes
    assert 'chr2' in chromosomes


def test_read_chromosomes_minimumcount(testdir, mock_testclass):
    bed = Path(__file__).parent.joinpath('siqchip-reads.bed')
    chromosomes = sc.read_chromosomes(bed, 2)
    assert 1 == len(chromosomes)
    assert 'chr1' in chromosomes

    
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
