import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from robtools import ChipexoQual as cq


@pytest.fixture
def mock_testclass():
    chipexoqual_datasets = cq.chipexoqual_datasets
    chipexoqual_dataset = cq.chipexoqual_dataset
    run = subprocess.run
    yield
    cq.chipexoqual_datasets = chipexoqual_datasets
    cq.chipexoqual_dataset = chipexoqual_dataset
    subprocess.run = run
    if 'CHIPEXOQUAL_BASE' in os.environ:
        del os.environ['CHIPEXOQUAL_BASE']


def test_chipexoqual(testdir, mock_testclass):
    datasets = Path(__file__).parent.joinpath('dataset.txt')
    cq.chipexoqual_datasets = MagicMock()
    runner = CliRunner()
    result = runner.invoke(cq.chipexoqual, ['--datasets', datasets])
    assert result.exit_code == 0
    cq.chipexoqual_datasets.assert_called_once_with(datasets, '', None, ())


def test_chipexoqual_parameters(testdir, mock_testclass):
    datasets = Path(__file__).parent.joinpath('dataset.txt')
    index = 1
    cq.chipexoqual_datasets = MagicMock()
    runner = CliRunner()
    result = runner.invoke(cq.chipexoqual,
                           ['--datasets', datasets, '--suffix', '-test', '--index', index, '-s', '1000000'])
    assert result.exit_code == 0
    cq.chipexoqual_datasets.assert_called_once_with(datasets, '-test', 1, ('-s', '1000000',))


def test_chipexoqual_datasetsnotexists(testdir, mock_testclass):
    datasets = 'dataset.txt'
    cq.chipexoqual_datasets = MagicMock()
    runner = CliRunner()
    result = runner.invoke(cq.chipexoqual, ['--datasets', datasets])
    assert result.exit_code != 0
    cq.chipexoqual_datasets.assert_not_called()


def test_chipexoqual_datasets(testdir, mock_testclass):
    datasets = Path(__file__).parent.joinpath('dataset.txt')
    cq.chipexoqual_dataset = MagicMock()
    cq.chipexoqual_datasets(datasets)
    cq.chipexoqual_dataset.assert_any_call('POLR2A', ['POLR2A_1', 'POLR2A_2'], '', ())
    cq.chipexoqual_dataset.assert_any_call('ASDURF', ['ASDURF_1', 'ASDURF_2'], '', ())
    cq.chipexoqual_dataset.assert_any_call('POLR1C', ['POLR1C_1', 'POLR1C_2'], '', ())


def test_chipexoqual_datasets_second(testdir, mock_testclass):
    datasets = Path(__file__).parent.joinpath('dataset.txt')
    cq.chipexoqual_dataset = MagicMock()
    cq.chipexoqual_datasets(datasets, index=1)
    cq.chipexoqual_dataset.assert_any_call('ASDURF', ['ASDURF_1', 'ASDURF_2'], '', ())


def test_chipexoqual_datasets_parameters(testdir, mock_testclass):
    datasets = Path(__file__).parent.joinpath('dataset.txt')
    chipexoqual_args = ('-s', '1000000',)
    cq.chipexoqual_dataset = MagicMock()
    cq.chipexoqual_datasets(datasets, '-test', chipexoqual_args=chipexoqual_args)
    cq.chipexoqual_dataset.assert_any_call('ASDURF', ['ASDURF_1', 'ASDURF_2'], '-test', chipexoqual_args)


def test_chipexoqual_dataset(testdir, mock_testclass):
    base = '/home/user/chipexoqual'
    os.environ['CHIPEXOQUAL_BASE'] = base
    dataset = 'PORL2A'
    samples = ['PORL2A_1', 'PORL2A_2']
    subprocess.run = MagicMock()
    cq.chipexoqual_dataset(dataset, samples)
    subprocess.run.assert_any_call(
        ['Rscript', base + '/chipexoqual.R', '-p', dataset + '_', 'PORL2A_1.bam', 'PORL2A_2.bam'], check=True)


def test_chipexoqual_dataset_parameters(testdir, mock_testclass):
    base = '/home/user/chipexoqual'
    os.environ['CHIPEXOQUAL_BASE'] = base
    dataset = 'PORL2A'
    samples = ['PORL2A_1', 'PORL2A_2']
    suffix = '-test'
    chipexoqual_args = ('-s', '1000000',)
    subprocess.run = MagicMock()
    cq.chipexoqual_dataset(dataset, samples, suffix, chipexoqual_args=chipexoqual_args)
    subprocess.run.assert_any_call(
        ['Rscript', base + '/chipexoqual.R', '-p', dataset + '_', '-s', '1000000', 'PORL2A_1-test.bam',
         'PORL2A_2-test.bam'], check=True)


def test_chipexoqual_noenvironment(testdir, mock_testclass):
    dataset = 'PORL2A'
    samples = ['PORL2A_1', 'PORL2A_2']
    subprocess.run = MagicMock()
    cq.chipexoqual_dataset(dataset, samples)
    subprocess.run.assert_any_call(['Rscript', 'chipexoqual.R', '-p', dataset + '_', 'PORL2A_1.bam', 'PORL2A_2.bam'],
                                   check=True)
