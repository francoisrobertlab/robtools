import logging
import os
from pathlib import Path
import subprocess
from unittest.mock import MagicMock, ANY

import click
from click.testing import CliRunner
import pytest

from robtools import MergeBam as mb


@pytest.fixture
def mock_testclass():
    merge_datasets = mb.merge_datasets
    merge_dataset = mb.merge_dataset
    run = subprocess.run
    yield
    mb.merge_datasets = merge_datasets
    mb.merge_dataset = merge_dataset
    subprocess.run = run
    

def create_file(*args, **kwargs):
    if 'stdout' in kwargs:
        outfile = kwargs['stdout']
        outfile.write('test')
    elif '-o' in args[0]:
        output = args[0][args[0].index('-o') + 1]
        with open(output, 'w') as outfile:
            outfile.write('test')


def test_mergebam(testdir, mock_testclass):
    datasets = Path(__file__).parent.joinpath('dataset.txt')
    mb.merge_datasets = MagicMock()
    runner = CliRunner()
    result = runner.invoke(mb.mergebam, ['-d', datasets])
    assert result.exit_code == 0
    mb.merge_datasets.assert_called_once_with(datasets, '', 1, None)


def test_mergebam_parameters(testdir, mock_testclass):
    datasets = Path(__file__).parent.joinpath('dataset.txt')
    suffix = '-dedup'
    threads = 3
    index = 1
    mb.merge_datasets = MagicMock()
    runner = CliRunner()
    result = runner.invoke(mb.mergebam, ['-d', datasets, '--suffix', suffix, '--threads', threads, '--index', index])
    assert result.exit_code == 0
    mb.merge_datasets.assert_called_once_with(datasets, suffix, threads, index)


def test_mergebam_mergenotexists(testdir, mock_testclass):
    datasets = 'dataset.txt'
    mb.merge_datasets = MagicMock()
    runner = CliRunner()
    result = runner.invoke(mb.mergebam, ['-d', datasets])
    assert result.exit_code != 0
    mb.merge_datasets.assert_not_called()


def test_merge_datasets(testdir, mock_testclass):
    datasets = Path(__file__).parent.joinpath('dataset.txt')
    mb.merge_dataset = MagicMock()
    mb.merge_datasets(datasets)
    mb.merge_dataset.assert_any_call('POLR2A', ['POLR2A_1', 'POLR2A_2'], '', 1)
    mb.merge_dataset.assert_any_call('ASDURF', ['ASDURF_1', 'ASDURF_2'], '', 1)
    mb.merge_dataset.assert_any_call('POLR1C', ['POLR1C_1', 'POLR1C_2'], '', 1)


def test_merge_datasets_parameters(testdir, mock_testclass):
    datasets = Path(__file__).parent.joinpath('dataset.txt')
    suffix = '-dedup'
    threads = 3
    mb.merge_dataset = MagicMock()
    mb.merge_datasets(datasets, suffix, threads)
    mb.merge_dataset.assert_any_call('POLR2A', ['POLR2A_1', 'POLR2A_2'], suffix, threads)
    mb.merge_dataset.assert_any_call('ASDURF', ['ASDURF_1', 'ASDURF_2'], suffix, threads)
    mb.merge_dataset.assert_any_call('POLR1C', ['POLR1C_1', 'POLR1C_2'], suffix, threads)


def test_merge_datasets_second(testdir, mock_testclass):
    datasets = Path(__file__).parent.joinpath('dataset.txt')
    mb.merge_dataset = MagicMock()
    mb.merge_datasets(datasets, index=1)
    mb.merge_dataset.assert_called_once_with('ASDURF', ['ASDURF_1', 'ASDURF_2'], '', 1)


def test_merge_dataset(testdir, mock_testclass):
    dataset = 'POLR2A'
    dataset_bam = dataset + '.bam'
    sample1 = dataset + '_1'
    sample1_bam = sample1 + '.bam'
    sample2 = dataset + '_2'
    sample2_bam = sample2 + '.bam'
    samples = [sample1, sample2]
    subprocess.run = MagicMock()
    mb.merge_dataset(dataset, samples)
    subprocess.run.assert_any_call(['samtools', 'index', sample1_bam], check=True)
    subprocess.run.assert_any_call(['samtools', 'index', sample2_bam], check=True)
    subprocess.run.assert_any_call(['samtools', 'merge', '-f', dataset_bam, sample1_bam, sample2_bam], check=True)


def test_merge_dataset_parameter(testdir, mock_testclass):
    suffix = '-dedup'
    dataset = 'POLR2A'
    dataset_bam = dataset + suffix + '.bam'
    sample1 = dataset + '_1'
    sample1_bam = sample1 + suffix + '.bam'
    sample2 = dataset + '_2'
    sample2_bam = sample2 + suffix + '.bam'
    samples = [sample1, sample2]
    threads = 3
    subprocess.run = MagicMock()
    mb.merge_dataset(dataset, samples, suffix, threads)
    subprocess.run.assert_any_call(['samtools', 'index', '-@', str(threads - 1), sample1_bam], check=True)
    subprocess.run.assert_any_call(['samtools', 'index', '-@', str(threads - 1), sample2_bam], check=True)
    subprocess.run.assert_any_call(['samtools', 'merge', '-f', '--threads', str(threads - 1), dataset_bam, sample1_bam, sample2_bam], check=True)
