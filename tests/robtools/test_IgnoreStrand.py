import logging
from pathlib import Path
from unittest.mock import MagicMock, ANY

import click
from click.testing import CliRunner
import pytest

from robtools import IgnoreStrand as igs
from robtools import Split as sb
from robtools.txt import Parser


@pytest.fixture
def mock_testclass():
    ignore_strand_samples = igs.ignore_strand_samples
    ignore_strand_sample_splits = igs.ignore_strand_sample_splits
    ignore_strand_sample = igs.ignore_strand_sample
    ignore_strand = igs.ignore_strand
    splits = sb.splits
    first = Parser.first
    yield
    igs.ignore_strand_samples = ignore_strand_samples
    igs.ignore_strand_sample_splits = ignore_strand_sample_splits
    igs.ignore_strand_sample = ignore_strand_sample
    igs.ignore_strand = ignore_strand
    sb.splits = splits
    Parser.first = first
    
    
def test_ignorestrand(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    igs.ignore_strand_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(igs.ignorestrand, ['-s', samples])
    assert result.exit_code == 0
    igs.ignore_strand_samples.assert_called_once_with(samples, '', '-forcov', None)


def test_ignorestrand_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    input_suffix = '-input'
    output_suffix = '-output'
    igs.ignore_strand_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(igs.ignorestrand, ['-s', samples, '-is', input_suffix, '-os', output_suffix])
    assert result.exit_code == 0
    igs.ignore_strand_samples.assert_called_once_with(samples, input_suffix, output_suffix, None)


def test_ignorestrand_samesuffix(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    input_suffix = '-input'
    igs.ignore_strand_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(igs.ignorestrand, ['-s', samples, '-is', input_suffix, '-os', input_suffix])
    assert result.exit_code > 0
    igs.ignore_strand_samples.assert_not_called()


def test_ignorestrand_onlyoutputsuffix(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    output_suffix = '-output'
    igs.ignore_strand_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(igs.ignorestrand, ['-s', samples, '-os', output_suffix])
    assert result.exit_code == 0
    igs.ignore_strand_samples.assert_called_once_with(samples, '', output_suffix, None)


def test_ignorestrand_second(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    index = 1
    igs.ignore_strand_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(igs.ignorestrand, ['-s', samples, '-i', index])
    assert result.exit_code == 0
    igs.ignore_strand_samples.assert_called_once_with(samples, '', '-forcov', index)


def test_ignorestrand_samplesnotexists(testdir, mock_testclass):
    samples = 'samples.txt'
    igs.ignore_strand_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(igs.ignorestrand, ['-s', samples])
    assert result.exit_code != 0
    igs.ignore_strand_samples.assert_not_called()


def test_ignore_strand_samples(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    Parser.first = MagicMock(return_value=samples)
    igs.ignore_strand_sample_splits = MagicMock()
    igs.ignore_strand_samples(samples_file)
    Parser.first.assert_called_once_with(samples_file)
    for sample in samples:
        igs.ignore_strand_sample_splits.assert_any_call(sample, '', '-forcov')


def test_ignore_strand_samples_parameters(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    input_suffix = '-input'
    output_suffix = '-output'
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    Parser.first = MagicMock(return_value=samples)
    igs.ignore_strand_sample_splits = MagicMock()
    igs.ignore_strand_samples(samples_file, input_suffix, output_suffix)
    Parser.first.assert_called_once_with(samples_file)
    for sample in samples:
        igs.ignore_strand_sample_splits.assert_any_call(sample, input_suffix, output_suffix)


def test_ignore_strand_samples_second(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    Parser.first = MagicMock(return_value=samples)
    igs.ignore_strand_sample_splits = MagicMock()
    igs.ignore_strand_samples(samples_file, index=1)
    Parser.first.assert_called_once_with(samples_file)
    igs.ignore_strand_sample_splits.assert_called_once_with(samples[1], '', '-forcov')

    
def test_ignore_strand_sample_splits(testdir, mock_testclass):
    sample = 'POLR2A'
    splits = ['POLR2A-100-110', 'POLR2A-120-130']
    igs.ignore_strand_sample = MagicMock()
    sb.splits = MagicMock(return_value=splits)
    igs.ignore_strand_sample_splits(sample)
    igs.ignore_strand_sample.assert_any_call(sample, '', '-forcov')
    for split in splits:
        igs.ignore_strand_sample.assert_any_call(split, '', '-forcov')


def test_ignore_strand_sample_splits_parameters(testdir, mock_testclass):
    sample = 'POLR2A'
    input_suffix = '-input'
    output_suffix = '-output'
    splits = ['POLR2A-100-110', 'POLR2A-120-130']
    igs.ignore_strand_sample = MagicMock()
    sb.splits = MagicMock(return_value=splits)
    igs.ignore_strand_sample_splits(sample, input_suffix, output_suffix)
    igs.ignore_strand_sample.assert_any_call(sample, input_suffix, output_suffix)
    for split in splits:
        igs.ignore_strand_sample.assert_any_call(split, input_suffix, output_suffix)

    
def test_ignore_strand_sample_splits_notsplits(testdir, mock_testclass):
    sample = 'POLR2A'
    splits = []
    igs.ignore_strand_sample = MagicMock()
    sb.splits = MagicMock(return_value=splits)
    igs.ignore_strand_sample_splits(sample)
    igs.ignore_strand_sample.assert_called_once_with(sample, '', '-forcov')

    
def test_ignore_strand_sample(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    forcov = sample + '-forcov.bed'
    igs.ignore_strand = MagicMock()
    igs.ignore_strand_sample(sample)
    igs.ignore_strand.assert_called_once_with(bed, forcov)


def test_ignore_strand_sample_split(testdir, mock_testclass):
    split = 'POLR2A-100-110'
    bed = split + '.bed'
    forcov = split + '-forcov.bed'
    igs.ignore_strand = MagicMock()
    igs.ignore_strand_sample(split)
    igs.ignore_strand.assert_called_once_with(bed, forcov)


def test_ignore_strand_sample_parameters(testdir, mock_testclass):
    sample = 'POLR2A'
    input_suffix = '-input'
    output_suffix = '-output'
    bed = sample + input_suffix + '.bed'
    forcov = sample + output_suffix + '.bed'
    igs.ignore_strand = MagicMock()
    igs.ignore_strand_sample(sample, input_suffix, output_suffix)
    igs.ignore_strand.assert_called_once_with(bed, forcov)

    
def test_ignore_strand(testdir, mock_testclass):
    bed = Path(__file__).parent.joinpath('sample.bed')
    forcov = 'POLR2A-forcov.bed'
    igs.ignore_strand(bed, forcov)
    with open(forcov, 'r') as infile:
        infile.readline() == 'chr1\t100\t150\ttest1\t1\t+\n'
        infile.readline() == 'chr1\t100\t150\ttest1\t1\t-\n'
        infile.readline() == 'chr2\t400\t450\ttest2\t2\t+\n'
        infile.readline() == 'chr2\t400\t450\ttest2\t2\t-\n'
        infile.readline() == 'chr3\t500\t650\ttest3\t3\t+\n'
        infile.readline() == 'chr3\t500\t650\ttest3\t3\t-\n'
        infile.readline() == 'chr4\t800\t750\ttest4\t4\t+\n'
        infile.readline() == 'chr4\t800\t750\ttest4\t4\t-\n'
        infile.readline() == 'chr5\t100\t150\ttest5\t1\t-\n'
        infile.readline() == 'chr5\t100\t150\ttest5\t1\t+\n'
        infile.readline() == 'chr6\t400\t450\ttest6\t2\t-\n'
        infile.readline() == 'chr6\t400\t450\ttest6\t2\t+\n'
        infile.readline() == 'chr7\t500\t650\ttest7\t3\t-\n'
        infile.readline() == 'chr7\t500\t650\ttest7\t3\t+\n'
        infile.readline() == 'chr8\t800\t750\ttest8\t4\t-\n'
        infile.readline() == 'chr8\t800\t750\ttest8\t4\t+\n'
