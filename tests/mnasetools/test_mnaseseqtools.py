import logging
from pathlib import Path
from unittest.mock import MagicMock, ANY

import click
from click.testing import CliRunner
import pytest

from mnasetools import mnasetools, DyadCoverage, DyadStatistics, FirstDyadPosition, FitDoubleGaussian, FitGaussian


@pytest.fixture
def mock_testclass():
    dyad_coverage = DyadCoverage.dyad_coverage
    dyad_statistics = DyadStatistics.dyad_statistics
    first_dyad_position = FirstDyadPosition.first_dyad_position
    fit_double_gaussian = FitDoubleGaussian.fit_double_gaussian
    fit_gaussian = FitGaussian.fit_gaussian
    yield
    DyadCoverage.dyad_coverage = dyad_coverage
    DyadStatistics.dyad_statistics = dyad_statistics
    FirstDyadPosition.first_dyad_position = first_dyad_position
    FitDoubleGaussian.fit_double_gaussian = fit_double_gaussian
    FitGaussian.fit_gaussian = fit_gaussian


def test_dyadcov(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genes = Path(__file__).parent.joinpath('firstdyad.txt')
    minp = -60
    maxp = 60
    smoothing = 10
    index = 2
    DyadCoverage.dyad_coverage = MagicMock()
    runner = CliRunner()
    result = runner.invoke(mnasetools.mnasetools, ['dyadcov', '--samples', samples, '--genes', genes, '--minp', minp, '--maxp', maxp])
    assert result.exit_code == 0
    DyadCoverage.dyad_coverage.assert_called_once_with(samples, genes, None, False, minp, maxp, None, None, None)


def test_dyadstatistics(testdir, mock_testclass):
    DyadStatistics.dyad_statistics = MagicMock()
    runner = CliRunner()
    result = runner.invoke(mnasetools.mnasetools, ['dyadstatistics'])
    assert result.exit_code == 0
    DyadStatistics.dyad_statistics.assert_called_once_with(-75, 75, 'dyad_statistics.txt', False)


def test_firstdyadposition(testdir, mock_testclass):
    genes = Path(__file__).parent.joinpath('firstdyad.txt')
    signal = Path(__file__).parent.joinpath('sample.bed')
    mind = 60
    maxd = 200
    output = 'output.txt'
    FirstDyadPosition.first_dyad_position = MagicMock()
    runner = CliRunner()
    result = runner.invoke(mnasetools.mnasetools, ['firstdyadposition', '--genes', genes, '--signal', signal, '--mind', mind, '--maxd', maxd, '--output', output])
    assert result.exit_code == 0
    FirstDyadPosition.first_dyad_position.assert_called_once_with(genes, signal, mind, maxd, output)


def test_fitdoublegaussian(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    FitDoubleGaussian.fit_double_gaussian = MagicMock()
    runner = CliRunner()
    result = runner.invoke(mnasetools.mnasetools, ['fitdoublegaussian', '--samples', samples])
    assert result.exit_code == 0
    FitDoubleGaussian.fit_double_gaussian.assert_called_once_with(samples, False, False, False, False, False, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)


def test_fitgaussian(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    FitGaussian.fit_gaussian = MagicMock()
    runner = CliRunner()
    result = runner.invoke(mnasetools.mnasetools, ['fitgaussian', '--samples', samples])
    assert result.exit_code == 0
    FitGaussian.fit_gaussian.assert_called_once_with(samples, False, False, False, False, None, None, None, None, None, None, None, None, None)
