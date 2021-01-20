import logging
import os
from pathlib import Path
from shutil import copyfile
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
    yield
    sb.siqchipbed_samples = siqchipbed_samples
    sb.siqchipbed_sample = siqchipbed_sample
    Bed.sort = sort
 
    
def temp2file(*args, **kwargs):
    input = args[0]
    output = args[1]
    copyfile(input, output)


def create_alignment(reverse, name, start, length):
    aln = MagicMock()
    aln.is_reverse = reverse
    aln.reference_name = name
    aln.reference_start = start
    aln.template_length = length
    return aln

    
def pysam_alignments(*args, **kwargs):
    alns = []
    alns.append(create_alignment(False, 'chr2L', 4612, 641))
    alns.append(create_alignment(False, 'chr3R', 4689, 507))
    alns.append(create_alignment(False, 'chr2L', 4703, 514))
    alns.append(create_alignment(False, 'chr3R', 4755, 481))
    alns.append(create_alignment(False, 'chr2L', 4797, 425))
    alns.append(create_alignment(False, 'chr3R', 4841, 325))
    alns.append(create_alignment(False, 'chrY_CP007108v1_random', 65943, 178))
    alns.append(create_alignment(True, 'chrY_CP007108v1_random', 63827, -664))
    alns.append(create_alignment(True, 'chrY_CP007108v1_random', 66070, -178))
    alns.append(create_alignment(False, 'chr3R', 4880, 0))
    return alns

    
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

    
@patch('pysam.AlignmentFile')
def test_siqchipbed_sample(mockalignmentfile, testdir, mock_testclass):
    sample = 'POLR2A'
    input = sample + '-dedup.bam'
    output = sample + '-reads.bed'
    Bed.sort = MagicMock(side_effect=temp2file)
    mockalignmentfile_instance = mockalignmentfile().__enter__()
    mockalignmentfile_instance.fetch.side_effect = pysam_alignments
    sb.siqchipbed_sample(sample)
    mockalignmentfile.assert_any_call(input, 'rb')
    mockalignmentfile_instance.fetch.assert_any_call(until_eof=True)
    Bed.sort.assert_called_with(ANY, output)
    with open(output, 'r') as outfile:
        assert 'chr2L\t4613\t5253\t640\n' == outfile.readline()
        assert 'chr3R\t4690\t5196\t506\n' == outfile.readline()
        assert 'chr2L\t4704\t5217\t513\n' == outfile.readline()
        assert 'chr3R\t4756\t5236\t480\n' == outfile.readline()
        assert 'chr2L\t4798\t5222\t424\n' == outfile.readline()
        assert 'chr3R\t4842\t5166\t324\n' == outfile.readline()
