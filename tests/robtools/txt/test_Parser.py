import logging
from pathlib import Path

import pytest

from robtools.txt import Parser as p


def test_columns():
    samples = Path(__file__).parent.parent.joinpath('samples.txt')
    columns = p.columns(samples)
    assert columns[0][0] == 'POLR2A'
    assert columns[0][1] == 'SRR8518913'
    assert columns[1][0] == 'ASDURF'
    assert columns[1][1] == 'SRX5322424'
    assert columns[2][0] == 'POLR1C'
    assert columns[2][1] == 'SRR8518915'


def test_columns_merge():
    samples = Path(__file__).parent.parent.joinpath('dataset.txt')
    columns = p.columns(samples)
    assert columns[0][0] == 'POLR2A'
    assert columns[0][1] == 'POLR2A_1'
    assert columns[0][2] == 'POLR2A_2'
    assert columns[1][0] == 'ASDURF'
    assert columns[1][1] == 'ASDURF_1'
    assert columns[1][2] == 'ASDURF_2'
    assert columns[2][0] == 'POLR1C'
    assert columns[2][1] == 'POLR1C_1'
    assert columns[2][2] == 'POLR1C_2'


def test_first():
    samples = Path(__file__).parent.parent.joinpath('samples.txt')
    names = p.first(samples)
    assert names == ['POLR2A', 'ASDURF', 'POLR1C']


def test_first_merge():
    samples = Path(__file__).parent.parent.joinpath('dataset.txt')
    names = p.first(samples)
    assert names == ['POLR2A', 'ASDURF', 'POLR1C']
