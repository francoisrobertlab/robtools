import logging
import os
from pathlib import Path
from shutil import copyfile
import subprocess
from unittest.mock import MagicMock, ANY

import click
from click.testing import CliRunner
import pytest

from mnasetools import FitGaussian as f
from robtools import Split as sb
from robtools.txt import Parser


@pytest.fixture
def mock_testclass():
    fit_gaussian = f.fit_gaussian
    fit_gaussian_sample = f.fit_gaussian_sample
    splits = sb.splits
    first = Parser.first
    yield
    f.fit_gaussian = fit_gaussian
    f.fit_gaussian_sample = fit_gaussian_sample
    sb.splits = splits
    Parser.first = first
    
    
def test_fitgaussian(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    f.fit_gaussian = MagicMock()
    runner = CliRunner()
    result = runner.invoke(f.fitgaussian, ['-s', samples])
    assert result.exit_code == 0
    f.fit_gaussian.assert_called_once_with(samples, False, False, False, False, None, None, None, None, None, None, None, None, None)


def test_fitgaussian_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    center = 0.4
    cmin = -10
    cmax = 10
    amp = 20
    amin = 2
    sigma = 15
    smin = 1.2
    suffix = 'test'
    f.fit_gaussian = MagicMock()
    runner = CliRunner()
    result = runner.invoke(f.fitgaussian, ['-s', samples, '--absolute', '--components', '--svg', '--verbose', '--center', center, '--cmin', cmin, '--cmax', cmax, '--amp', amp, '--amin', amin, '--sigma', sigma, '--smin', smin, '--suffix', suffix])
    assert result.exit_code == 0
    f.fit_gaussian.assert_called_once_with(samples, True, True, True, True, center, cmin, cmax, amp, amin, sigma, smin, suffix, None)


def test_fitgaussian_second(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    index = 1
    f.fit_gaussian = MagicMock()
    runner = CliRunner()
    result = runner.invoke(f.fitgaussian, ['-s', samples, '-i', index])
    assert result.exit_code == 0
    f.fit_gaussian.assert_called_once_with(samples, False, False, False, False, None, None, None, None, None, None, None, None, index)


def test_fitgaussian_samplesnotexists(testdir, mock_testclass):
    samples = 'samples.txt'
    f.fit_gaussian = MagicMock()
    runner = CliRunner()
    result = runner.invoke(f.fitgaussian, ['-s', samples])
    assert result.exit_code != 0
    f.fit_gaussian.assert_not_called()


def test_fit_gaussian(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    splits1 = ['POLR2A-100-110', 'POLR2A-120-130']
    splits2 = ['ASDURF-100-110', 'ASDURF-120-130']
    splits3 = ['POLR1C-100-110', 'POLR1C-120-130']
    Parser.first = MagicMock(return_value=samples)
    sb.splits = MagicMock(side_effect=[splits1, splits2, splits3])
    f.fit_gaussian_sample = MagicMock()
    f.fit_gaussian(samples_file)
    Parser.first.assert_called_once_with(samples_file)
    for sample in samples:
        sb.splits.assert_any_call(sample)
        f.fit_gaussian_sample.assert_any_call(sample, False, False, False, False, None, None, None, None, None, None, None, None)
    for split in splits1:
        f.fit_gaussian_sample.assert_any_call(split, False, False, False, False, None, None, None, None, None, None, None, None)
    for split in splits2:
        f.fit_gaussian_sample.assert_any_call(split, False, False, False, False, None, None, None, None, None, None, None, None)
    for split in splits3:
        f.fit_gaussian_sample.assert_any_call(split, False, False, False, False, None, None, None, None, None, None, None, None)


def test_fit_gaussian_parameters(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    center = 0.4
    cmin = -10
    cmax = 10
    amp = 20
    amin = 2
    sigma = 15
    smin = 1.2
    suffix = 'test'
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    splits1 = ['POLR2A-100-110', 'POLR2A-120-130']
    splits2 = ['ASDURF-100-110', 'ASDURF-120-130']
    splits3 = ['POLR1C-100-110', 'POLR1C-120-130']
    Parser.first = MagicMock(return_value=samples)
    sb.splits = MagicMock(side_effect=[splits1, splits2, splits3])
    f.fit_gaussian_sample = MagicMock()
    f.fit_gaussian(samples_file, True, True, True, True, center, cmin, cmax, amp, amin, sigma, smin, suffix)
    Parser.first.assert_called_once_with(samples_file)
    for sample in samples:
        sb.splits.assert_any_call(sample)
        f.fit_gaussian_sample.assert_any_call(sample, True, True, True, True, center, cmin, cmax, amp, amin, sigma, smin, suffix)
    for split in splits1:
        f.fit_gaussian_sample.assert_any_call(split, True, True, True, True, center, cmin, cmax, amp, amin, sigma, smin, suffix)
    for split in splits2:
        f.fit_gaussian_sample.assert_any_call(split, True, True, True, True, center, cmin, cmax, amp, amin, sigma, smin, suffix)
    for split in splits3:
        f.fit_gaussian_sample.assert_any_call(split, True, True, True, True, center, cmin, cmax, amp, amin, sigma, smin, suffix)


def test_fit_gaussian_second(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    splits = ['ASDURF-100-110', 'ASDURF-120-130']
    Parser.first = MagicMock(return_value=samples)
    sb.splits = MagicMock(return_value=splits)
    f.fit_gaussian_sample = MagicMock()
    f.fit_gaussian(samples_file, index=1)
    Parser.first.assert_called_once_with(samples_file)
    sb.splits.assert_called_once_with(samples[1])
    f.fit_gaussian_sample.assert_any_call(samples[1], False, False, False, False, None, None, None, None, None, None, None, None)
    for split in splits:
        f.fit_gaussian_sample.assert_any_call(split, False, False, False, False, None, None, None, None, None, None, None, None)
