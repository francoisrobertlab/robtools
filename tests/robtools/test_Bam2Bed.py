import logging
import os
from pathlib import Path
from shutil import copyfile
import subprocess
from unittest.mock import MagicMock, ANY

import click
from click.testing import CliRunner
import pytest

from robtools import Bam2Bed as bb
from robtools.bed import Bed


@pytest.fixture
def mock_testclass():
    bam2bed_samples = bb.bam2bed_samples
    bam2bed_sample = bb.bam2bed_sample
    bam2bed_unpaired = bb.bam2bed_unpaired
    bam2bedpe = bb.bam2bedpe
    bedpe2bed = bb.bedpe2bed
    sort = Bed.sort
    run = subprocess.run
    yield 
    bb.bam2bed_samples = bam2bed_samples
    bb.bam2bed_sample = bam2bed_sample
    bb.bam2bed_unpaired = bam2bed_unpaired
    bb.bam2bedpe = bam2bedpe
    bb.bedpe2bed = bedpe2bed
    Bed.sort = sort
    subprocess.run = run
    
    
def create_file(*args, **kwargs):
    if 'stdout' in kwargs:
        outfile = kwargs['stdout']
        outfile.write('test')
    elif '-o' in args[0]:
        output = args[0][args[0].index('-o') + 1]
        with open(output, 'w') as outfile:
            outfile.write('test')


def create_file_bam2bedpe(*args, **kwargs):
    output = args[1]
    with open(output, 'w') as outfile:
        outfile.write('test')


def create_file_bedsort(*args, **kwargs):
    output = args[1]
    with open(output, 'w') as outfile:
         outfile.write('test bed sort')


def test_bam2bed(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    threads = 1
    bb.bam2bed_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(bb.bam2bed, ['-s', samples])
    assert result.exit_code == 0
    bb.bam2bed_samples.assert_called_once_with(samples, True, threads, '-dedup', None)


def test_bam2bed_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    threads = 2
    input_suffix = '-test'
    index = 1
    bb.bam2bed_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(bb.bam2bed, ['-s', samples, '--unpaired', '--threads', threads, '-is', input_suffix, '--index', index])
    assert result.exit_code == 0
    bb.bam2bed_samples.assert_called_once_with(samples, False, threads, input_suffix, index)


def test_bam2bed_samples(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    bb.bam2bed_sample = MagicMock()
    bb.bam2bed_samples(samples)
    bb.bam2bed_sample.assert_any_call('POLR2A', True, None, '')
    bb.bam2bed_sample.assert_any_call('ASDURF', True, None, '')
    bb.bam2bed_sample.assert_any_call('POLR1C', True, None, '')


def test_bam2bed_samples_all_threads(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    threads = 2
    input_suffix = '-test'
    bb.bam2bed_sample = MagicMock()
    bb.bam2bed_samples(samples, threads=threads, input_suffix=input_suffix)
    bb.bam2bed_sample.assert_any_call('POLR2A', True, threads, input_suffix)
    bb.bam2bed_sample.assert_any_call('ASDURF', True, threads, input_suffix)
    bb.bam2bed_sample.assert_any_call('POLR1C', True, threads, input_suffix)


def test_bam2bed_samples_all_notpaired(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    threads = 2
    input_suffix = '-test'
    bb.bam2bed_sample = MagicMock()
    bb.bam2bed_samples(samples, False, threads, input_suffix)
    bb.bam2bed_sample.assert_any_call('POLR2A', False, threads, input_suffix)
    bb.bam2bed_sample.assert_any_call('ASDURF', False, threads, input_suffix)
    bb.bam2bed_sample.assert_any_call('POLR1C', False, threads, input_suffix)


def test_bam2bed_samples_second_threads(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    threads = 2
    input_suffix = '-test'
    bb.bam2bed_sample = MagicMock()
    bb.bam2bed_samples(samples, True, threads, input_suffix, 1)
    bb.bam2bed_sample.assert_called_once_with('ASDURF', True, threads, input_suffix)

    
def test_bam2bed_sample_paired(testdir, mock_testclass):
    sample = 'POLR2A'
    bam = sample + '.bam'
    bed = sample + '.bed'
    threads = 2
    bb.bam2bedpe = MagicMock(side_effect=create_file_bam2bedpe)
    bb.bedpe2bed = MagicMock()
    bb.bam2bed_sample(sample, True, threads)
    bb.bam2bedpe.assert_called_with(bam, ANY, threads)
    bb.bedpe2bed.assert_called_with(ANY, bed)
    assert bb.bam2bedpe.call_args.args[1] == bb.bedpe2bed.call_args.args[0]


def test_bam2bed_sample_paired_inputsuffix(testdir, mock_testclass):
    sample = 'POLR2A'
    input_suffix = '-test'
    bam = sample + input_suffix + '.bam'
    bed = sample + '.bed'
    threads = 2
    bb.bam2bedpe = MagicMock(side_effect=create_file_bam2bedpe)
    bb.bedpe2bed = MagicMock()
    bb.bam2bed_sample(sample, True, threads, input_suffix)
    bb.bam2bedpe.assert_called_with(bam, ANY, threads)
    bb.bedpe2bed.assert_called_with(ANY, bed)
    assert bb.bam2bedpe.call_args.args[1] == bb.bedpe2bed.call_args.args[0]


def test_bam2bed_sample_notpaired(testdir, mock_testclass):
    sample = 'POLR2A'
    bam = sample + '.bam'
    bed = sample + '.bed'
    bb.bam2bed_unpaired = MagicMock()
    bb.bam2bed_sample(sample, False)
    bb.bam2bed_unpaired.assert_called_with(bam, bed)


def test_bam2bed_sample_notpaired_inputsuffix(testdir, mock_testclass):
    sample = 'POLR2A'
    input_suffix = '-test'
    bam = sample + input_suffix + '.bam'
    bed = sample + '.bed'
    bb.bam2bed_unpaired = MagicMock()
    bb.bam2bed_sample(sample, False, input_suffix=input_suffix)
    bb.bam2bed_unpaired.assert_called_with(bam, bed)


def test_bam2bed_sample_unpaired(testdir, mock_testclass):
    sample = 'POLR2A'
    bam = sample + '.bam'
    bed = sample + '.bed'
    subprocess.run = MagicMock(side_effect=create_file)
    Bed.sort = MagicMock(side_effect=create_file_bedsort)
    bb.bam2bed_unpaired(bam, bed)
    subprocess.run.assert_any_call(['bedtools', 'bamtobed', '-i', bam], stdout=ANY, check=True)
    Bed.sort.assert_called_with(ANY, bed)
    assert os.path.exists(bed)
    with open(bed, 'r') as infile:
        assert infile.readline() == 'test bed sort'

    
def test_bam2bedpe(testdir, mock_testclass):
    bam = 'POLR2A.bam'
    bedpe = 'POLR2A.bedpe'
    threads = 2
    subprocess.run = MagicMock(side_effect=create_file)
    bb.bam2bedpe(bam, bedpe, threads)
    subprocess.run.assert_any_call(['samtools', 'sort', '-n', '--threads', str(threads - 1), '-o', ANY, bam], check=True)
    subprocess.run.assert_any_call(['bedtools', 'bamtobed', '-bedpe', '-mate1', '-i', ANY], stdout=ANY, check=True)
    assert subprocess.run.call_args_list[0].args[0][6] == subprocess.run.call_args_list[1].args[0][5]
    assert os.path.exists(bedpe)


def test_bam2bedpe_singlethread(testdir, mock_testclass):
    bam = 'POLR2A.bam'
    bedpe = 'POLR2A.bedpe'
    threads = 1
    subprocess.run = MagicMock(side_effect=create_file)
    bb.bam2bedpe(bam, bedpe, threads)
    subprocess.run.assert_any_call(['samtools', 'sort', '-n', '-o', ANY, bam], check=True)
    subprocess.run.assert_any_call(['bedtools', 'bamtobed', '-bedpe', '-mate1', '-i', ANY], stdout=ANY, check=True)
    assert subprocess.run.call_args_list[0].args[0][4] == subprocess.run.call_args_list[1].args[0][5]
    assert os.path.exists(bedpe)


def test_bedpe2bed(testdir, mock_testclass):
    bedpe = 'POLR2A.bedpe'
    sample_bedpe = Path(__file__).parent.joinpath('sample.bedpe')
    copyfile(sample_bedpe, bedpe)
    bed = 'POLR2A.bed'
    Bed.sort = MagicMock(side_effect=copyfile)
    bb.bedpe2bed(bedpe, bed)
    Bed.sort.assert_called_with(ANY, bed)
    assert os.path.exists(bed)
    with open(bed, 'r') as infile:
        assert infile.readline() == 'chr1\t100\t250\ttest1\t1\t+\t0\ttest0\n'
        assert infile.readline() == 'chr2\t300\t450\ttest2\t2\t+\t1\ttest1\n'
        assert infile.readline() == 'chr3\t500\t650\ttest3\t3\t+\t2\ttest2\n'
        assert infile.readline() == 'chr4\t700\t850\ttest4\t4\t+\t3\ttest3\n'
        assert infile.readline() == 'chr5\t100\t250\ttest5\t1\t-\t4\ttest4\n'
        assert infile.readline() == 'chr6\t300\t450\ttest6\t2\t-\t5\ttest5\n'
        assert infile.readline() == 'chr7\t500\t650\ttest7\t3\t-\t6\ttest6\n'
        assert infile.readline() == 'chr8\t700\t850\ttest8\t4\t-\t7\ttest7\n'
        assert infile.readline() == ''
