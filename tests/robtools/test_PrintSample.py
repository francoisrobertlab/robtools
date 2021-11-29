import logging
import os
from pathlib import Path
from shutil import copyfile
import subprocess
from unittest.mock import MagicMock, ANY

import click
from click.testing import CliRunner
import pytest

from robtools import PrintSample as ps


@pytest.fixture
def mock_testclass():
    print_sample = ps.print_sample
    yield 
    ps.print_sample = print_sample
    
    
def test_printsample(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    index = 0
    ps.print_sample = MagicMock()
    runner = CliRunner()
    result = runner.invoke(ps.printsample, ['-s', samples, '-i', index])
    assert result.exit_code == 0
    ps.print_sample.assert_called_once_with(samples, False, '', index)


def test_printsample_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    suffix = '-dedup'
    index = 0
    ps.print_sample = MagicMock()
    runner = CliRunner()
    result = runner.invoke(ps.printsample, ['-s', samples, '--replicates', '--suffix', suffix, '-i', index])
    assert result.exit_code == 0
    ps.print_sample.assert_called_once_with(samples, True, suffix, index)


def test_printsample_samplesnotexists(testdir, mock_testclass):
    samples = 'samples.txt'
    index = 0
    ps.print_sample = MagicMock()
    runner = CliRunner()
    result = runner.invoke(ps.printsample, ['-s', samples, '-i', index])
    assert result.exit_code > 0
    ps.print_sample.assert_not_called()


def test_printsample_noindex(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    ps.print_sample = MagicMock()
    runner = CliRunner()
    result = runner.invoke(ps.printsample, ['-s', samples])
    assert result.exit_code > 0
    ps.print_sample.assert_not_called()


def test_print_sample_first(testdir, capsys, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    index = 0
    ps.print_sample(samples, index=index)
    captured = capsys.readouterr()
    assert captured.out == "POLR2A\n"


def test_print_sample_firstsuffix(testdir, capsys, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    index = 0
    ps.print_sample(samples, suffix='-dedup', index=index)
    captured = capsys.readouterr()
    assert captured.out == "POLR2A-dedup\n"


def test_print_sample_firstreplicates(testdir, capsys, mock_testclass):
    samples = Path(__file__).parent.joinpath('dataset.txt')
    index = 0
    ps.print_sample(samples, replicates=True, index=index)
    captured = capsys.readouterr()
    assert captured.out == "POLR2A\tPOLR2A_1\tPOLR2A_2\n"


def test_print_sample_firstreplicatessuffix(testdir, capsys, mock_testclass):
    samples = Path(__file__).parent.joinpath('dataset.txt')
    index = 0
    ps.print_sample(samples, replicates=True, suffix='-dedup', index=index)
    captured = capsys.readouterr()
    assert captured.out == "POLR2A-dedup\tPOLR2A_1-dedup\tPOLR2A_2-dedup\n"


def test_print_sample_second(testdir, capsys, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    index = 1
    ps.print_sample(samples, index=index)
    captured = capsys.readouterr()
    assert captured.out == "ASDURF\n"


def test_print_sample_secondsuffix(testdir, capsys, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    index = 1
    ps.print_sample(samples, suffix='-dedup', index=index)
    captured = capsys.readouterr()
    assert captured.out == "ASDURF-dedup\n"


def test_print_sample_secondreplicates(testdir, capsys, mock_testclass):
    samples = Path(__file__).parent.joinpath('dataset.txt')
    index = 1
    ps.print_sample(samples, replicates=True, index=index)
    captured = capsys.readouterr()
    assert captured.out == "ASDURF\tASDURF_1\tASDURF_2\n"


def test_print_sample_secondreplicatessuffix(testdir, capsys, mock_testclass):
    samples = Path(__file__).parent.joinpath('dataset.txt')
    index = 1
    ps.print_sample(samples, replicates=True, suffix='-dedup', index=index)
    captured = capsys.readouterr()
    assert captured.out == "ASDURF-dedup\tASDURF_1-dedup\tASDURF_2-dedup\n"
