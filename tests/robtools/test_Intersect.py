import logging
import os
from pathlib import Path
from shutil import copyfile
import subprocess
from unittest.mock import MagicMock, ANY

import click
from click.testing import CliRunner
import pytest

from robtools import Intersect as ib
from robtools.bed import Bed


@pytest.fixture
def mock_testclass():
    intersect_samples = ib.intersect_samples
    annotations_length = ib.annotations_length
    intersect_sample = ib.intersect_sample
    sort = Bed.sort
    run = subprocess.run
    remove = os.remove
    yield
    ib.intersect_samples = intersect_samples
    ib.annotations_length = annotations_length
    ib.intersect_sample = intersect_sample
    Bed.sort = sort
    subprocess.run = run
    os.remove = remove
    
    
def create_file(*args, **kwargs):
    if 'stdout' in kwargs:
        outfile = kwargs['stdout']
        outfile.write('test')
    elif '-o' in args[0]:
        output = args[0][args[0].index('-o') + 1]
        with open(output, 'w') as outfile:
            outfile.write('test')


def create_intersectbed(*args, **kwargs):
    outfile = kwargs['stdout']
    intersect_source = Path(__file__).parent.joinpath('sample-intersect.bed')
    with open(intersect_source, 'r') as infile:
        for line in infile:
           outfile.write(line)     


def test_intersect(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('intersect.txt')
    annotations = Path(__file__).parent.joinpath('annotations.bed')
    ib.intersect_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(ib.intersect, ['-s', samples, '-a' , annotations])
    assert result.exit_code == 0
    ib.intersect_samples.assert_called_once_with(samples, annotations, None)


def test_intersect_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('intersect.txt')
    annotations = Path(__file__).parent.joinpath('annotations.bed')
    index = 1
    ib.intersect_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(ib.intersect, ['-s', samples, '-a' , annotations, '--index', index])
    assert result.exit_code == 0
    ib.intersect_samples.assert_called_once_with(samples, annotations, index)


def test_intersect_samples(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('intersect.txt')
    annotations = Path(__file__).parent.joinpath('annotations.bed')
    annotations_length = 6
    ib.annotations_length = MagicMock(return_value=annotations_length)
    ib.intersect_sample = MagicMock()
    ib.intersect_samples(samples, annotations)
    ib.annotations_length.assert_called_once_with(annotations)
    ib.intersect_sample.assert_any_call('POLR2A', 'POLR2A-inter', annotations, annotations_length)
    ib.intersect_sample.assert_any_call('ASDURF', 'ASDURF-inter', annotations, annotations_length)
    ib.intersect_sample.assert_any_call('POLR1C', 'POLR1C-inter', annotations, annotations_length)


def test_intersect_samples_second(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('intersect.txt')
    annotations = Path(__file__).parent.joinpath('annotations.bed')
    annotations_length = 6
    ib.annotations_length = MagicMock(return_value=annotations_length)
    ib.intersect_sample = MagicMock()
    ib.intersect_samples(samples, annotations, 1)
    ib.annotations_length.assert_called_once_with(annotations)
    ib.intersect_sample.assert_called_once_with('ASDURF', 'ASDURF-inter', annotations, annotations_length)


def test_annotations_length():
    annotations = Path(__file__).parent.joinpath('annotations.bed')
    annotations_length = ib.annotations_length(annotations)
    assert annotations_length == 8


def test_annotations_length_smaller():
    annotations = Path(__file__).parent.joinpath('annotations_smaller.bed')
    annotations_length = ib.annotations_length(annotations)
    assert annotations_length == 6


def test_intersect_sample(testdir, mock_testclass):
    sample = 'POLR2A'
    tag = sample + '-intersect'
    annotations = 'annotations.bed'
    annotation_length = 8
    bed = sample + '.bed'
    tag_bed = tag + '.bed'
    subprocess.run = MagicMock(side_effect=create_intersectbed)
    Bed.sort = MagicMock(side_effect=create_file(['-o', tag_bed]))
    os_remove = os.remove
    os.remove = MagicMock()
    ib.intersect_sample(sample, tag, annotations, annotation_length)
    subprocess.run.assert_called_once_with(['bedtools', 'intersect', '-a', annotations, '-b', bed, '-wb'], stdout=ANY, check=True)
    Bed.sort.assert_called_once_with(ANY, tag_bed)
    with open(Bed.sort.call_args.args[0], 'r') as infile:
        assert infile.readline() == 'chr1\t110\t120\ttest1\t1\t+\n'
        assert infile.readline() == 'chr2\t415\t425\ttest2\t2\t+\n'
        assert infile.readline() == 'chr3\t520\t530\ttest3\t3\t+\n'
        assert infile.readline() == 'chr4\t820\t830\ttest4\t4\t+\n'
        assert infile.readline() == 'chr5\t110\t120\ttest1\t1\t-\n'
        assert infile.readline() == 'chr6\t415\t425\ttest2\t2\t-\n'
        assert infile.readline() == 'chr7\t520\t530\ttest3\t3\t-\n'
        assert infile.readline() == 'chr8\t820\t830\ttest4\t4\t-\n'
        assert infile.readline() == ''
    for remove_args in os.remove.call_args_list:
        os_remove(remove_args.args[0])
