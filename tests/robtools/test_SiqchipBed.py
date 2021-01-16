import logging
import os
from pathlib import Path
from shutil import copyfile
import subprocess
from unittest.mock import MagicMock, call, ANY, patch

import click
from click.testing import CliRunner, make_input_stream
from more_itertools.more import side_effect
import pytest

from robtools import SiqchipBed as sb
from robtools.bed import Bed


@pytest.fixture
def mock_testclass():
    siqchipbed_samples = sb.siqchipbed_samples
    siqchipbed_sample = sb.siqchipbed_sample
    sort = Bed.sort
    run = subprocess.run
    yield
    sb.siqchipbed_samples = siqchipbed_samples
    sb.siqchipbed_sample = siqchipbed_sample
    Bed.sort = sort
    subprocess.run = run
            
    
def temp2file(*args, **kwargs):
    input = args[0]
    output = args[1]
    copyfile(input, output)


def create_sam(*args, **kwargs):
    if 'stdout' in kwargs:
        output = kwargs['stdout']
        copyfile(Path(__file__).parent.joinpath('sample.sam'), output)
    elif '-o' in args[0]:
        output = args[0][args[0].index('-o') + 1]
        copyfile(Path(__file__).parent.joinpath('sample.sam'), output)

    
def test_siqchipbed(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    sb.siqchipbed_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(sb.siqchipbed, ['--samples', samples])
    assert result.exit_code == 0
    sb.siqchipbed_samples.assert_called_once_with(samples, '-dedup', '-reads', None)


def test_siqchipbed_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    input_suffix = '-myinput'
    output_suffix = '-myoutput'
    index = 1
    sb.siqchipbed_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(sb.siqchipbed, ['--samples', samples, '--input-suffix', input_suffix, '--output-suffix', output_suffix, '--index', index])
    assert result.exit_code == 0
    sb.siqchipbed_samples.assert_called_once_with(samples, input_suffix, output_suffix, index)


def test_siqchipbed_samplesnotexists(testdir, mock_testclass):
    samples = 'samples.txt'
    sb.siqchipbed_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(sb.siqchipbed, ['--samples', samples])
    assert result.exit_code > 0
    sb.siqchipbed_samples.assert_not_called()


def test_siqchipbed_samples(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    sb.siqchipbed_sample = MagicMock()
    sb.siqchipbed_samples(samples)
    sb.siqchipbed_sample.assert_any_call('POLR2A', '-dedup', '-reads')
    sb.siqchipbed_sample.assert_any_call('ASDURF', '-dedup', '-reads')
    sb.siqchipbed_sample.assert_any_call('POLR1C', '-dedup', '-reads')


def test_siqchip_samples_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    input_suffix = '-myinput'
    output_suffix = '-myoutput'
    index = 1
    sb.siqchipbed_sample = MagicMock()
    sb.siqchipbed_samples(samples, input_suffix, output_suffix, index)
    sb.siqchipbed_sample.assert_called_once_with('ASDURF', input_suffix, output_suffix)

    
def test_siqchipbed_sample(testdir, mock_testclass):
    sample = 'POLR2A'
    input = sample + '-dedup.bam'
    output = sample + '-reads.bed'
    Bed.sort = MagicMock(side_effect=temp2file)
    subprocess.run = MagicMock(side_effect=create_sam)
    sb.siqchipbed_sample(sample)
    subprocess.run.assert_called_with(['samtools', 'view', '-o', ANY, input], check=True)
    assert isinstance(subprocess.run.call_args[0][0][3], str)
    Bed.sort.assert_called_with(ANY, output)
    with open(output, 'r') as outfile:
        assert 'chr2L\t4613\t5253\t640\n' == outfile.readline()
        assert 'chr3R\t4690\t5196\t506\n' == outfile.readline()
        assert 'chr2L\t4704\t5217\t513\n' == outfile.readline()
        assert 'chr3R\t4756\t5236\t480\n' == outfile.readline()
        assert 'chr2L\t4798\t5222\t424\n' == outfile.readline()
        assert 'chr3R\t4842\t5166\t324\n' == outfile.readline()
