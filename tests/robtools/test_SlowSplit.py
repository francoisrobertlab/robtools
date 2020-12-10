import logging
import os
from pathlib import Path
from unittest.mock import MagicMock, ANY

import click
from click.testing import CliRunner
import pytest

from robtools import SlowSplit as ss


@pytest.fixture
def mock_testclass():
    split_samples = ss.split_samples
    split_sample = ss.split_sample
    filter_bed_by_length = ss.filter_bed_by_length
    yield
    ss.split_samples = split_samples
    ss.split_sample = split_sample
    ss.filter_bed_by_length = filter_bed_by_length
    

def test_slowsplit(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    ss.split_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(ss.slowsplit, ['-s', samples])
    assert result.exit_code == 0
    ss.split_samples.assert_called_once_with(samples, None, 10, 100, 500)


def test_slowsplit_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    ss.split_samples = MagicMock()
    binlength = 20
    binminlength = 200
    binmaxlength = 400
    index = 1
    ss.split_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(ss.slowsplit, ['-s', samples, '--binLength', binlength, '--binMinLength', binminlength, '--binMaxLength', binmaxlength, '--index', index])
    assert result.exit_code == 0
    ss.split_samples.assert_called_once_with(samples, index, binlength, binminlength, binmaxlength)


def test_slowsplit_samplesnotexists(testdir, mock_testclass):
    samples = 'samples.txt'
    ss.split_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(ss.slowsplit, ['-s', samples])
    assert result.exit_code != 0
    ss.split_samples.assert_not_called()


def test_split_samples(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    ss.split_sample = MagicMock()
    ss.split_samples(samples)
    ss.split_sample.assert_any_call('POLR2A', 10, 100, 500)
    ss.split_sample.assert_any_call('ASDURF', 10, 100, 500)
    ss.split_sample.assert_any_call('POLR1C', 10, 100, 500)


def test_split_samples_second(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    ss.split_sample = MagicMock()
    ss.split_samples(samples, 1)
    ss.split_sample.assert_called_once_with('ASDURF', 10, 100, 500)


def test_split_samples_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    ss.split_sample = MagicMock()
    binlength = 20
    binminlength = 200
    binmaxlength = 400
    ss.split_samples(samples, binlength=binlength, binminlength=binminlength, binmaxlength=binmaxlength)
    ss.split_sample.assert_any_call('POLR2A', binlength, binminlength, binmaxlength)
    ss.split_sample.assert_any_call('ASDURF', binlength, binminlength, binmaxlength)
    ss.split_sample.assert_any_call('POLR1C', binlength, binminlength, binmaxlength)


def test_split_samples_second_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    ss.split_sample = MagicMock()
    binlength = 20
    binminlength = 200
    binmaxlength = 400
    ss.split_samples(samples, 1, binlength, binminlength, binmaxlength)
    ss.split_sample.assert_called_once_with('ASDURF', binlength, binminlength, binmaxlength)


def test_split_sample(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    ss.filter_bed_by_length = MagicMock()
    binlength = 10
    binminlength = 100
    binmaxlength = 200
    ss.split_sample(sample, binlength, binminlength, binmaxlength)
    ss.filter_bed_by_length.assert_any_call(bed, sample + '-100-110.bed', 100, 110)
    ss.filter_bed_by_length.assert_any_call(bed, sample + '-110-120.bed', 110, 120)
    ss.filter_bed_by_length.assert_any_call(bed, sample + '-120-130.bed', 120, 130)
    ss.filter_bed_by_length.assert_any_call(bed, sample + '-130-140.bed', 130, 140)
    ss.filter_bed_by_length.assert_any_call(bed, sample + '-140-150.bed', 140, 150)
    ss.filter_bed_by_length.assert_any_call(bed, sample + '-150-160.bed', 150, 160)
    ss.filter_bed_by_length.assert_any_call(bed, sample + '-160-170.bed', 160, 170)
    ss.filter_bed_by_length.assert_any_call(bed, sample + '-170-180.bed', 170, 180)
    ss.filter_bed_by_length.assert_any_call(bed, sample + '-180-190.bed', 180, 190)
    ss.filter_bed_by_length.assert_any_call(bed, sample + '-190-200.bed', 190, 200)
    assert ss.filter_bed_by_length.call_count == 10


def test_split_sample_shorterlastbin(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    ss.filter_bed_by_length = MagicMock()
    binlength = 10
    binminlength = 155
    binmaxlength = 200
    ss.split_sample(sample, binlength, binminlength, binmaxlength)
    ss.filter_bed_by_length.assert_any_call(bed, sample + '-155-165.bed', 155, 165)
    ss.filter_bed_by_length.assert_any_call(bed, sample + '-165-175.bed', 165, 175)
    ss.filter_bed_by_length.assert_any_call(bed, sample + '-175-185.bed', 175, 185)
    ss.filter_bed_by_length.assert_any_call(bed, sample + '-185-195.bed', 185, 195)
    ss.filter_bed_by_length.assert_any_call(bed, sample + '-195-200.bed', 195, 200)
    assert ss.filter_bed_by_length.call_count == 5


def test_split_sample_largerbin(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    ss.filter_bed_by_length = MagicMock()
    binlength = 100
    binminlength = 110
    binmaxlength = 190
    ss.split_sample(sample, binlength, binminlength, binmaxlength)
    ss.filter_bed_by_length.assert_called_once_with(bed, sample + '-110-190.bed', 110, 190)


def test_filter_bed_by_length(testdir, mock_testclass):
    bed = Path(__file__).parent.joinpath('sample-slowsplit.bed')
    out = 'out.bed'
    bin_start = 100
    bin_end = 130
    ss.filter_bed_by_length(bed, out, bin_start, bin_end)
    with open(out, 'r') as infile:
        assert infile.readline() == 'chr1\t100\t229\ttest1\t1\t+\n'
        assert infile.readline() == 'chr4\t800\t900\ttest4\t4\t+\n'
        assert infile.readline() == 'chr5\t100\t220\ttest5\t1\t-\n'
        assert infile.readline() == 'chr8\t800\t910\ttest8\t4\t-\n'
        assert infile.readline() == ''


def test_filter_bed_by_length_2(testdir, mock_testclass):
    bed = Path(__file__).parent.joinpath('sample-slowsplit.bed')
    out = 'out.bed'
    bin_start = 100
    bin_end = 121
    ss.filter_bed_by_length(bed, out, bin_start, bin_end)
    with open(out, 'r') as infile:
        assert infile.readline() == 'chr4\t800\t900\ttest4\t4\t+\n'
        assert infile.readline() == 'chr5\t100\t220\ttest5\t1\t-\n'
        assert infile.readline() == 'chr8\t800\t910\ttest8\t4\t-\n'
        assert infile.readline() == ''


def test_filter_bed_by_length_3(testdir, mock_testclass):
    bed = Path(__file__).parent.joinpath('sample-slowsplit.bed')
    out = 'out.bed'
    bin_start = 100
    bin_end = 110
    ss.filter_bed_by_length(bed, out, bin_start, bin_end)
    with open(out, 'r') as infile:
        assert infile.readline() == 'chr4\t800\t900\ttest4\t4\t+\n'
        assert infile.readline() == ''
