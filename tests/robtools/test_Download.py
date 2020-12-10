import logging
import os
from pathlib import Path
import subprocess
from unittest.mock import MagicMock

import click
from click.testing import CliRunner
import pytest

from robtools import Download as d


@pytest.fixture
def mock_testclass():
    download_samples = d.download_samples
    download_sample = d.download_sample
    run = subprocess.run
    yield
    d.download_samples = download_samples
    d.download_sample = download_sample
    subprocess.run = run
    
    
def create_file(*args):
    for name in args:
        with open(name, 'w') as outfile:
            outfile.write('test')


def test_download(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    mem = '100MB'
    threads = 6
    d.download_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(d.download, ['-s', samples])
    assert result.exit_code == 0
    d.download_samples.assert_called_once_with(samples, True, threads, mem, None)


def test_download_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    mem = '200MB'
    threads = 8
    index = 1
    d.download_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(d.download, ['-s', samples, '--slow', '--threads', threads, '--mem', mem, '--index', index])
    assert result.exit_code == 0
    d.download_samples.assert_called_once_with(samples, False, threads, mem, 1)


def test_download_samples(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    mem = '100MB'
    d.download_sample = MagicMock()
    d.download_samples(samples)
    d.download_sample.assert_any_call('POLR2A', 'SRR8518913', True, None, mem)
    d.download_sample.assert_any_call('ASDURF', 'SRX5322424', True, None, mem)
    d.download_sample.assert_any_call('POLR1C', 'SRR8518915', True, None, mem)


def test_download_samples_allfast(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    mem = '200MB'
    threads = 2
    d.download_sample = MagicMock()
    d.download_samples(samples, True, threads, mem)
    d.download_sample.assert_any_call('POLR2A', 'SRR8518913', True, threads, mem)
    d.download_sample.assert_any_call('ASDURF', 'SRX5322424', True, threads, mem)
    d.download_sample.assert_any_call('POLR1C', 'SRR8518915', True, threads, mem)


def test_download_samples_allslow(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    mem = '200MB'
    threads = 2
    d.download_sample = MagicMock()
    d.download_samples(samples, False, threads, mem)
    d.download_sample.assert_any_call('POLR2A', 'SRR8518913', False, threads, mem)
    d.download_sample.assert_any_call('ASDURF', 'SRX5322424', False, threads, mem)
    d.download_sample.assert_any_call('POLR1C', 'SRR8518915', False, threads, mem)


def test_download_samples_second(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    mem = '100MB'
    d.download_sample = MagicMock()
    d.download_samples(samples, index=1)
    d.download_sample.assert_called_once_with('ASDURF', 'SRX5322424', True, None, mem)


def test_download_sample_singleend(testdir, mock_testclass):
    srr = 'SRR8518913'
    mem = '100MB'
    threads = 1
    subprocess.run = MagicMock(side_effect=create_file(srr + '_1.fastq'))
    d.download_sample('POLR2A', srr, True, threads, mem)
    subprocess.run.assert_called_with(['fasterq-dump', '--split-files', '--threads', str(threads), '--mem', mem, srr], check=True)
    assert os.path.exists('POLR2A_1.fastq')


def test_download_sample_pairedend(testdir, mock_testclass):
    srr = 'SRR8518913'
    mem = '100MB'
    threads = 1
    subprocess.run = MagicMock(side_effect=create_file(srr + '_1.fastq', srr + '_2.fastq'))
    d.download_sample('POLR2A', srr, True, threads, mem)
    subprocess.run.assert_called_with(['fasterq-dump', '--split-files', '--threads', str(threads), '--mem', mem, srr], check=True)
    assert os.path.exists('POLR2A_1.fastq')
    assert os.path.exists('POLR2A_2.fastq')


def test_download_sample_slow_singleend(testdir, mock_testclass):
    srr = 'SRR8518913'
    mem = '100MB'
    threads = 1
    subprocess.run = MagicMock(side_effect=create_file(srr + '_1.fastq'))
    d.download_sample('POLR2A', srr, False, threads, mem)
    subprocess.run.assert_called_with(['fastq-dump', '--split-files', srr], check=True)
    assert os.path.exists('POLR2A_1.fastq')


def test_download_sample_slow_pairedend(testdir, mock_testclass):
    srr = 'SRR8518913'
    mem = '100MB'
    threads = 1
    subprocess.run = MagicMock(side_effect=create_file(srr + '_1.fastq', srr + '_2.fastq'))
    d.download_sample('POLR2A', srr, False, threads, mem)
    subprocess.run.assert_called_with(['fastq-dump', '--split-files', srr], check=True)
    assert os.path.exists('POLR2A_1.fastq')
    assert os.path.exists('POLR2A_2.fastq')


def test_download_sample_failed(testdir, mock_testclass):
    srr = 'SRR8518913'
    mem = '100MB'
    threads = 1
    subprocess.run = MagicMock(side_effect=subprocess.CalledProcessError('Could not download file', ['test']))
    with pytest.raises(subprocess.CalledProcessError):
        d.download_sample('POLR2A', srr, True, threads, mem)
    subprocess.run.assert_called_with(['fasterq-dump', '--split-files', '--threads', str(threads), '--mem', mem, srr], check=True)
    assert not os.path.exists('POLR2A_1.fastq')
    assert not os.path.exists('POLR2A_2.fastq')
