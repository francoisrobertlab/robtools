import logging
import os
from pathlib import Path
from shutil import copyfile
import subprocess
from unittest.mock import MagicMock, ANY

import click
from click.testing import CliRunner
import pytest

from robtools import ShiftAnnotations as sa
from robtools.txt import Parser


@pytest.fixture
def mock_testclass():
    shift_annotations_samples = sa.shift_annotations_samples
    shift_annotations_sample = sa.shift_annotations_sample
    first = Parser.first
    yield
    sa.shift_annotations_samples = shift_annotations_samples
    sa.shift_annotations_sample = shift_annotations_sample
    Parser.first = first
    
    
def create_file(*args, **kwargs):
    if 'stdout' in kwargs:
        outfile = kwargs['stdout']
        outfile.write('test')
    elif '-o' in args[0]:
        output = args[0][args[0].index('-o') + 1]
        with open(output, 'w') as outfile:
            outfile.write('test')


def test_shiftannotations(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    sa.shift_annotations_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(sa.shiftannotations, ['-s', samples])
    assert result.exit_code == 0
    sa.shift_annotations_samples.assert_called_once_with(samples, '', '-forcov', None, ())


def test_shiftannotations_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = 'sacCer3.chrom.sizes'
    copyfile(Path(__file__).parent.joinpath('sizes.txt'), genome)
    input_suffix = '-input'
    output_suffix = '-output'
    minus = '2'
    plus = '-2'
    index = 1
    sa.shift_annotations_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(sa.shiftannotations, ['-s', samples, '-is', input_suffix, '-os', output_suffix, '-g', genome, '-m', minus, '-p', plus, '-i', index])
    assert result.exit_code == 0
    sa.shift_annotations_samples.assert_called_once_with(samples, input_suffix, output_suffix, index, ('-g', genome, '-m', minus, '-p', plus,))


def test_shiftannotations_samesuffix(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    input_suffix = '-input'
    sa.shift_annotations_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(sa.shiftannotations, ['-s', samples, '-is', input_suffix, '-os', input_suffix])
    assert result.exit_code > 0
    sa.shift_annotations_samples.assert_not_called()


def test_shiftannotations_onlyoutputsuffix(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    output_suffix = '-output'
    sa.shift_annotations_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(sa.shiftannotations, ['-s', samples, '-os', output_suffix])
    assert result.exit_code == 0
    sa.shift_annotations_samples.assert_called_once_with(samples, '', output_suffix, None, ())


def test_shiftannotations_second(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    index = 1
    sa.shift_annotations_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(sa.shiftannotations, ['-s', samples, '-i', index])
    assert result.exit_code == 0
    sa.shift_annotations_samples.assert_called_once_with(samples, '', '-forcov', index, ())


def test_shiftannotations_samplesnotexists(testdir, mock_testclass):
    samples = 'samples.txt'
    sa.shift_annotations_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(sa.shiftannotations, ['-s', samples])
    assert result.exit_code != 0
    sa.shift_annotations_samples.assert_not_called()


def test_shift_annotations_samples(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    Parser.first = MagicMock(return_value=samples)
    sa.shift_annotations_sample = MagicMock()
    sa.shift_annotations_samples(samples_file)
    Parser.first.assert_called_once_with(samples_file)
    for sample in samples:
        sa.shift_annotations_sample.assert_any_call(sample, '', '-forcov', ())


def test_shift_annotations_samples_parameters(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    genome = 'sacCer3.chrom.sizes'
    input_suffix = '-input'
    output_suffix = '-output'
    minus = '2'
    plus = '-2'
    Parser.first = MagicMock(return_value=samples)
    sa.shift_annotations_sample = MagicMock()
    sa.shift_annotations_samples(samples_file, input_suffix, output_suffix, bedtools_args=('-g', genome, '-m', minus, '-p', plus,))
    Parser.first.assert_called_once_with(samples_file)
    for sample in samples:
        sa.shift_annotations_sample.assert_any_call(sample, input_suffix, output_suffix, ('-g', genome, '-m', minus, '-p', plus,))


def test_shift_annotations_samples_second(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    Parser.first = MagicMock(return_value=samples)
    sa.shift_annotations_sample = MagicMock()
    sa.shift_annotations_samples(samples_file, index=1)
    Parser.first.assert_called_once_with(samples_file)
    sa.shift_annotations_sample.assert_any_call(samples[1], '', '-forcov', ())

    
def test_shift_annotations_sample(testdir, mock_testclass):
    sample = 'POLR2A'
    src_bed = Path(__file__).parent.joinpath('sample.bed')
    bed = sample + '.bed'
    forcov = sample + '-forcov.bed'
    copyfile(src_bed, bed)
    subprocess.run = MagicMock(side_effect=create_file)
    sa.shift_annotations_sample(sample)
    subprocess.run.assert_called_once_with(['bedtools', 'shift', '-i', bed], stdout=ANY, check=True)
    assert os.path.exists(forcov)
    with open(forcov, 'r') as infile:
        assert 'test' == infile.readline()


def test_shift_annotations_sample_parameters(testdir, mock_testclass):
    sample = 'POLR2A'
    genome = 'sacCer3.chrom.sizes'
    input_suffix = '-input'
    output_suffix = '-output'
    minus = '2'
    plus = '-2'
    src_bed = Path(__file__).parent.joinpath('sample.bed')
    bed = sample + input_suffix + '.bed'
    forcov = sample + output_suffix + '.bed'
    copyfile(src_bed, bed)
    subprocess.run = MagicMock(side_effect=create_file)
    sa.shift_annotations_sample(sample, input_suffix, output_suffix, ('-g', genome, '-m', minus, '-p', plus,))
    subprocess.run.assert_called_once_with(['bedtools', 'shift', '-i', bed, '-g', genome, '-m', minus, '-p', plus], stdout=ANY, check=True)
    assert os.path.exists(forcov)
    with open(forcov, 'r') as infile:
        assert 'test' == infile.readline()
