import subprocess
from unittest.mock import MagicMock

import pytest

from robtools.bam import Bam


@pytest.fixture
def mock_testclass():
    run = subprocess.run
    yield
    subprocess.run = run


def test_sort(mock_testclass):
    bam = 'sample.bam'
    output = 'sample-out.bam'
    subprocess.run = MagicMock()
    Bam.sort(bam, output)
    subprocess.run.assert_called_with(['samtools', 'sort', '-o', output, bam], check=True)


def test_sort_by_readname(mock_testclass):
    bam = 'sample.bam'
    output = 'sample-out.bam'
    subprocess.run = MagicMock()
    Bam.sort_by_readname(bam, output)
    subprocess.run.assert_called_with(['samtools', 'sort', '-n', '-o', output, bam], check=True)
