import logging
import os
from pathlib import Path
from shutil import copyfile
import subprocess
from unittest.mock import MagicMock, ANY

import click
from click.testing import CliRunner
import pytest

from mnaseseqtools import FitDoubleGaussian as f
from robtools import Split as sb
from robtools.txt import Parser


@pytest.fixture
def mock_testclass():
    fit_double_gaussian = f.fit_double_gaussian
    fit_double_gaussian_sample = f.fit_double_gaussian_sample
    splits = sb.splits
    first = Parser.first
    yield
    f.fit_double_gaussian = fit_double_gaussian
    f.fit_double_gaussian_sample = fit_double_gaussian_sample
    sb.splits = splits
    Parser.first = first
    
    
def test_fitdoublegaussian(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    f.fit_double_gaussian = MagicMock()
    runner = CliRunner()
    result = runner.invoke(f.fitdoublegaussian, ['-s', samples])
    assert result.exit_code == 0
    f.fit_double_gaussian.assert_called_once_with(samples, False, False, False, False, False, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)


def test_fitdoublegaussian_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    center1 = 2.4
    cmin1 = -10
    cmax1 = 10
    amp1 = 20
    amin1 = 2
    sigma1 = 8
    smin1 = 1.2
    center2 = -1.8
    cmin2 = -9
    cmax2 = 9
    amp2 = 18
    amin2 = 1.4
    sigma2 = 7
    smin2 = 1.1
    suffix = 'test'
    f.fit_double_gaussian = MagicMock()
    runner = CliRunner()
    result = runner.invoke(f.fitdoublegaussian, ['-s', samples, '--absolute', '--components', '--gaussian', '--svg', '--verbose', '--center1', center1, '--cmin1', cmin1, '--cmax1', cmax1, '--amp1', amp1, '--amin1', amin1, '--sigma1', sigma1, '--smin1', smin1, '--center2', center2, '--cmin2', cmin2, '--cmax2', cmax2, '--amp2', amp2, '--amin2', amin2, '--sigma2', sigma2, '--smin2', smin2, '--suffix', suffix])
    assert result.exit_code == 0
    f.fit_double_gaussian.assert_called_once_with(samples, True, True, True, True, True, center1, cmin1, cmax1, amp1, amin1, sigma1, smin1, center2, cmin2, cmax2, amp2, amin2, sigma2, smin2, suffix, None)


def test_fitdoublegaussian_second(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    index = 1
    f.fit_double_gaussian = MagicMock()
    runner = CliRunner()
    result = runner.invoke(f.fitdoublegaussian, ['-s', samples, '-i', index])
    assert result.exit_code == 0
    f.fit_double_gaussian.assert_called_once_with(samples, False, False, False, False, False, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, index)


def test_fitdoublegaussian_samplesnotexists(testdir, mock_testclass):
    samples = 'samples.txt'
    f.fit_double_gaussian = MagicMock()
    runner = CliRunner()
    result = runner.invoke(f.fitdoublegaussian, ['-s', samples])
    assert result.exit_code != 0
    f.fit_double_gaussian.assert_not_called()


def test_fit_double_gaussian(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    splits1 = ['POLR2A-100-110', 'POLR2A-120-130']
    splits2 = ['ASDURF-100-110', 'ASDURF-120-130']
    splits3 = ['POLR1C-100-110', 'POLR1C-120-130']
    Parser.first = MagicMock(return_value=samples)
    sb.splits = MagicMock(side_effect=[splits1, splits2, splits3])
    f.fit_double_gaussian_sample = MagicMock()
    f.fit_double_gaussian(samples_file)
    Parser.first.assert_called_once_with(samples_file)
    for sample in samples:
        sb.splits.assert_any_call(sample)
        f.fit_double_gaussian_sample.assert_any_call(sample, False, False, False, False, False, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
    for split in splits1:
        f.fit_double_gaussian_sample.assert_any_call(split, False, False, False, False, False, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
    for split in splits2:
        f.fit_double_gaussian_sample.assert_any_call(split, False, False, False, False, False, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
    for split in splits3:
        f.fit_double_gaussian_sample.assert_any_call(split, False, False, False, False, False, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)


def test_fit_double_gaussian_parameters(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    center1 = 2.4
    cmin1 = -10
    cmax1 = 10
    amp1 = 20
    amin1 = 2
    sigma1 = 8
    smin1 = 1.2
    center2 = -1.8
    cmin2 = -9
    cmax2 = 9
    amp2 = 18
    amin2 = 1.4
    sigma2 = 7
    smin2 = 1.1
    suffix = 'test'
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    splits1 = ['POLR2A-100-110', 'POLR2A-120-130']
    splits2 = ['ASDURF-100-110', 'ASDURF-120-130']
    splits3 = ['POLR1C-100-110', 'POLR1C-120-130']
    Parser.first = MagicMock(return_value=samples)
    sb.splits = MagicMock(side_effect=[splits1, splits2, splits3])
    f.fit_double_gaussian_sample = MagicMock()
    f.fit_double_gaussian(samples_file, True, True, True, True, True, center1, cmin1, cmax1, amp1, amin1, sigma1, smin1, center2, cmin2, cmax2, amp2, amin2, sigma2, smin2, suffix)
    Parser.first.assert_called_once_with(samples_file)
    for sample in samples:
        sb.splits.assert_any_call(sample)
        f.fit_double_gaussian_sample.assert_any_call(sample, True, True, True, True, True, center1, cmin1, cmax1, amp1, amin1, sigma1, smin1, center2, cmin2, cmax2, amp2, amin2, sigma2, smin2, suffix)
    for split in splits1:
        f.fit_double_gaussian_sample.assert_any_call(split, True, True, True, True, True, center1, cmin1, cmax1, amp1, amin1, sigma1, smin1, center2, cmin2, cmax2, amp2, amin2, sigma2, smin2, suffix)
    for split in splits2:
        f.fit_double_gaussian_sample.assert_any_call(split, True, True, True, True, True, center1, cmin1, cmax1, amp1, amin1, sigma1, smin1, center2, cmin2, cmax2, amp2, amin2, sigma2, smin2, suffix)
    for split in splits3:
        f.fit_double_gaussian_sample.assert_any_call(split, True, True, True, True, True, center1, cmin1, cmax1, amp1, amin1, sigma1, smin1, center2, cmin2, cmax2, amp2, amin2, sigma2, smin2, suffix)


def test_fit_double_gaussian_second(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    splits = ['ASDURF-100-110', 'ASDURF-120-130']
    Parser.first = MagicMock(return_value=samples)
    sb.splits = MagicMock(return_value=splits)
    f.fit_double_gaussian_sample = MagicMock()
    f.fit_double_gaussian(samples_file, index=1)
    Parser.first.assert_called_once_with(samples_file)
    sb.splits.assert_called_once_with(samples[1])
    f.fit_double_gaussian_sample.assert_any_call(samples[1], False, False, False, False, False, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
    for split in splits:
        f.fit_double_gaussian_sample.assert_any_call(split, False, False, False, False, False, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
