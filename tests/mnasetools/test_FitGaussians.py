from pathlib import Path
from unittest.mock import MagicMock

from click.testing import CliRunner
import pytest

from mnasetools import FitGaussians as f
from robtools.txt import Parser


@pytest.fixture
def mock_testclass():
    fit_gaussians = f.fit_gaussians
    fit_gaussians_sample = f.fit_gaussians_sample
    first = Parser.first
    yield
    f.fit_gaussians = fit_gaussians
    f.fit_gaussians_sample = fit_gaussians_sample
    Parser.first = first
    
    
def test_fitgaussians(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    f.fit_gaussians = MagicMock()
    runner = CliRunner()
    result = runner.invoke(f.fitgaussians, ['-s', samples])
    assert result.exit_code == 0
    f.fit_gaussians.assert_called_once_with(samples, False, False, False, False, False, 1, None, None, None, None, None, None)


def test_fitgaussians_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    count = 4
    amin = 10
    amax = 900
    smin = 0.1
    smax = 2
    suffix = 'test'
    f.fit_gaussians = MagicMock()
    runner = CliRunner()
    result = runner.invoke(f.fitgaussians, ['-s', samples, '--components', '--gaussian', '--svg', '--verbose', '--curves', '--count', count, '--amin', amin, '--amax', amax, '--smin', smin, '--smax', smax, '--suffix', suffix])
    assert result.exit_code == 0
    f.fit_gaussians.assert_called_once_with(samples, True, True, True, True, True, count, amin, amax, smin, smax, suffix, None)


def test_fitgaussians_second(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    index = 1
    f.fit_gaussians = MagicMock()
    runner = CliRunner()
    result = runner.invoke(f.fitgaussians, ['-s', samples, '-i', index])
    assert result.exit_code == 0
    f.fit_gaussians.assert_called_once_with(samples, False, False, False, False, False, 1, None, None, None, None, None, index)


def test_fitgaussians_samplesnotexists(testdir, mock_testclass):
    samples = 'samples.txt'
    f.fit_gaussians = MagicMock()
    runner = CliRunner()
    result = runner.invoke(f.fitgaussians, ['-s', samples])
    assert result.exit_code != 0
    f.fit_gaussians.assert_not_called()


def test_fit_gaussians(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    Parser.first = MagicMock(return_value=samples)
    f.fit_gaussians_sample = MagicMock()
    f.fit_gaussians(samples_file)
    Parser.first.assert_called_once_with(samples_file)
    for sample in samples:
        f.fit_gaussians_sample.assert_any_call(sample, False, False, False, False, False, 1, None, None, None, None, None)


def test_fit_gaussians_parameters(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    count = 4
    amin = 10
    amax = 900
    smin = 0.1
    smax = 2
    suffix = 'test'
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    Parser.first = MagicMock(return_value=samples)
    f.fit_gaussians_sample = MagicMock()
    f.fit_gaussians(samples_file, True, True, True, True, True, count, amin, amax, smin, smax, suffix)
    Parser.first.assert_called_once_with(samples_file)
    for sample in samples:
        f.fit_gaussians_sample.assert_any_call(sample, True, True, True, True, True, count, amin, amax, smin, smax, suffix)


def test_fit_gaussians_second(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    Parser.first = MagicMock(return_value=samples)
    f.fit_gaussians_sample = MagicMock()
    f.fit_gaussians(samples_file, index=1)
    Parser.first.assert_called_once_with(samples_file)
    f.fit_gaussians_sample.assert_any_call(samples[1], False, False, False, False, False, 1, None, None, None, None, None)
