import logging
from pathlib import Path
from unittest.mock import MagicMock, ANY

import click
from click.testing import CliRunner
import pytest

from mnaseseqtools import PrepareGenomeCoverage as p
from seqtools import Split as sb
from seqtools.txt import Parser


@pytest.fixture
def mock_testclass():
    prep_genomecov = p.prep_genomecov
    sample_splits_prepgenomecov = p.sample_splits_prepgenomecov
    prepgenomecov_sample = p.prepgenomecov_sample
    center_annotations = p.center_annotations
    splits = sb.splits
    first = Parser.first
    yield
    p.prep_genomecov = prep_genomecov
    p.sample_splits_prepgenomecov = sample_splits_prepgenomecov
    p.prepgenomecov_sample = prepgenomecov_sample
    p.center_annotations = center_annotations
    sb.splits = splits
    Parser.first = first
    
    
def test_prepgenomecov(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    p.prep_genomecov = MagicMock()
    runner = CliRunner()
    result = runner.invoke(p.prepgenomecov, ['-s', samples])
    assert result.exit_code == 0
    p.prep_genomecov.assert_called_once_with(samples, None)


def test_prepgenomecov_second(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    index = 1
    p.prep_genomecov = MagicMock()
    runner = CliRunner()
    result = runner.invoke(p.prepgenomecov, ['-s', samples, '-i', index])
    assert result.exit_code == 0
    p.prep_genomecov.assert_called_once_with(samples, index)


def test_prepgenomecov_samplesnotexists(testdir, mock_testclass):
    samples = 'samples.txt'
    p.prep_genomecov = MagicMock()
    runner = CliRunner()
    result = runner.invoke(p.prepgenomecov, ['-s', samples])
    assert result.exit_code != 0
    p.prep_genomecov.assert_not_called()


def test_prep_genomecov(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    Parser.first = MagicMock(return_value=samples)
    p.sample_splits_prepgenomecov = MagicMock()
    p.prep_genomecov(samples_file)
    Parser.first.assert_called_once_with(samples_file)
    for sample in samples:
        p.sample_splits_prepgenomecov.assert_any_call(sample)


def test_prep_genomecov_second(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    Parser.first = MagicMock(return_value=samples)
    p.sample_splits_prepgenomecov = MagicMock()
    p.prep_genomecov(samples_file, 1)
    Parser.first.assert_called_once_with(samples_file)
    p.sample_splits_prepgenomecov.assert_called_once_with(samples[1])

    
def test_sample_splits_prepgenomecov(testdir, mock_testclass):
    sample = 'POLR2A'
    splits = ['POLR2A-100-110', 'POLR2A-120-130']
    p.prepgenomecov_sample = MagicMock()
    sb.splits = MagicMock(return_value=splits)
    p.sample_splits_prepgenomecov(sample)
    p.prepgenomecov_sample.assert_any_call(sample)
    for split in splits:
        p.prepgenomecov_sample.assert_any_call(split)

    
def test_sample_splits_prepgenomecov_notsplits(testdir, mock_testclass):
    sample = 'POLR2A'
    splits = []
    p.prepgenomecov_sample = MagicMock()
    sb.splits = MagicMock(return_value=splits)
    p.sample_splits_prepgenomecov(sample)
    p.prepgenomecov_sample.assert_called_once_with(sample)

    
def test_prepgenomecov_sample(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    forcov = sample + '-forcov.bed'
    p.center_annotations = MagicMock()
    p.prepgenomecov_sample(sample)
    p.center_annotations.assert_called_once_with(bed, forcov)


def test_prepgenomecov_sample_split(testdir, mock_testclass):
    split = 'POLR2A-100-110'
    bed = split + '.bed'
    forcov = split + '-forcov.bed'
    p.center_annotations = MagicMock()
    p.prepgenomecov_sample(split)
    p.center_annotations.assert_called_once_with(bed, forcov)

    
def test_center_annotations(testdir, mock_testclass):
    bed = Path(__file__).parent.joinpath('sample.bed')
    forcov = 'POLR2A-forcov.bed'
    p.center_annotations(bed, forcov)
    with open(forcov, 'r') as infile:
        infile.readline() == 'chr1\t125\t126\ttest1\t1\t+\n'
        infile.readline() == 'chr2\t425\t426\ttest2\t2\t+\n'
        infile.readline() == 'chr3\t575\t576\ttest3\t3\t+\n'
        infile.readline() == 'chr4\t775\t775\ttest4\t4\t+\n'
        infile.readline() == 'chr5\t125\t126\ttest5\t1\t-\n'
        infile.readline() == 'chr6\t425\t426\ttest6\t2\t-\n'
        infile.readline() == 'chr7\t575\t576\ttest7\t3\t-\n'
        infile.readline() == 'chr8\t875\t776\ttest8\t4\t-\n'