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
    ps.print_sample.assert_called_once_with(samples, '', index)


def test_printsample_suffix(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    suffix = '-dedup'
    index = 0
    ps.print_sample = MagicMock()
    runner = CliRunner()
    result = runner.invoke(ps.printsample, ['-s', samples, '--suffix', suffix, '-i', index])
    assert result.exit_code == 0
    ps.print_sample.assert_called_once_with(samples, suffix, index)


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
    ps.print_sample(samples, '-dedup', index)
    captured = capsys.readouterr()
    assert captured.out == "POLR2A-dedup\n"


def test_print_sample_second(testdir, capsys, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    index = 1
    ps.print_sample(samples, index=index)
    captured = capsys.readouterr()
    assert captured.out == "ASDURF\n"


def test_print_sample_secondsuffix(testdir, capsys, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    index = 1
    ps.print_sample(samples, '-dedup', index)
    captured = capsys.readouterr()
    assert captured.out == "ASDURF-dedup\n"
