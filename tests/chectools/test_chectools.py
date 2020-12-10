import logging
from pathlib import Path
from unittest.mock import MagicMock, ANY

import click
from click.testing import CliRunner
import pytest

from chectools import chectools, DyadPosition


@pytest.fixture
def mock_testclass():
    dyad_position = DyadPosition.dyad_position
    yield
    DyadPosition.dyad_position = dyad_position


def test_dyadposition(testdir, mock_testclass):
    genes = Path(__file__).parent.joinpath('firstdyad.txt')
    signal = Path(__file__).parent.joinpath('sample.bed')
    dyad = 2
    mind = 141
    maxd = 191
    output = 'output.txt'
    DyadPosition.dyad_position = MagicMock()
    runner = CliRunner()
    result = runner.invoke(chectools.chectools, ['dyadposition', '--genes', genes, '--signal', signal, '--output', output])
    assert result.exit_code == 0
    DyadPosition.dyad_position.assert_called_once_with(genes, signal, dyad, mind, maxd, output)
