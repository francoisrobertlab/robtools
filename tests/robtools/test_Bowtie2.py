import logging
import math
import os
from pathlib import Path
from shutil import copyfile
import subprocess
from unittest.mock import MagicMock, call, ANY

import click
from click.testing import CliRunner
from more_itertools.more import side_effect
import pytest

from robtools import Bowtie2 as b
from robtools.seq import Fastq


@pytest.fixture
def mock_testclass():
    bowtie_samples = b.bowtie_samples
    bowtie_sample = b.bowtie_sample
    run_bowtie = b.run_bowtie
    sort = b.sort
    fastq = Fastq.fastq
    run = subprocess.run
    yield
    b.bowtie_samples = bowtie_samples
    b.bowtie_sample = bowtie_sample
    b.run_bowtie = run_bowtie
    b.sort = sort
    Fastq.fastq = fastq
    subprocess.run = run
    

def create_file(*args, **kwargs):
    if 'stdout' in kwargs:
        outfile = kwargs['stdout']
        outfile.write('test')
    elif '-o' in args[0]:
        output = args[0][args[0].index('-o') + 1]
        with open(output, 'w') as outfile:
            outfile.write('test')
    elif '-S' in args[0]:
        output = args[0][args[0].index('-S') + 1]
        with open(output, 'w') as outfile:
            outfile.write('test')


def test_bowtie2(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    b.bowtie_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(b.bowtie2, ['--samples', samples])
    assert result.exit_code == 0
    b.bowtie_samples.assert_called_once_with(samples, 1, '', None, ())


def test_bowtie2_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    threads = 2
    output_suffix = '-sacCer'
    index = 1
    b.bowtie_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(b.bowtie2, ['--samples', samples, '-x', 'sacCer3.fa', '--threads', threads, '--output-suffix', output_suffix, '--index', index])
    assert result.exit_code == 0
    b.bowtie_samples.assert_called_once_with(samples, threads, output_suffix, index, ('-x', 'sacCer3.fa',))


def test_bowtie2_filenotexists(testdir, mock_testclass):
    samples = 'samples.txt'
    b.bowtie_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(b.bowtie2, ['--samples', samples])
    assert result.exit_code != 0
    b.bowtie_samples.assert_not_called()


def test_bowtie_samples(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    b.bowtie_sample = MagicMock()
    b.bowtie_samples(samples)
    b.bowtie_sample.assert_any_call('POLR2A', None, '', ())
    b.bowtie_sample.assert_any_call('ASDURF', None, '', ())
    b.bowtie_sample.assert_any_call('POLR1C', None, '', ())


def test_bowtie_samples_second(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    b.bowtie_sample = MagicMock()
    b.bowtie_samples(samples, index=1)
    b.bowtie_sample.assert_called_once_with('ASDURF', None, '', ())


def test_bowtie_samples_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    threads = 2
    output_suffix = '-sacCer'
    bowtie_args = ('-x', 'sacCer3.fa',)
    b.bowtie_sample = MagicMock()
    b.bowtie_samples(samples, threads, output_suffix, bowtie_args=bowtie_args)
    b.bowtie_sample.assert_any_call('POLR2A', threads, output_suffix, bowtie_args)
    b.bowtie_sample.assert_any_call('ASDURF', threads, output_suffix, bowtie_args)
    b.bowtie_sample.assert_any_call('POLR1C', threads, output_suffix, bowtie_args)


def test_bowtie_sample(testdir, mock_testclass):
    sample = 'PORL2A'
    bam = sample + '.bam'
    fastq = sample + '_1.fastq'
    fastq2 = sample + '_2.fastq'
    b.run_bowtie = MagicMock()
    Fastq.fastq = MagicMock(side_effect=[fastq, fastq2])
    b.bowtie_sample(sample)
    Fastq.fastq.assert_any_call(sample, 1)
    Fastq.fastq.assert_any_call(sample, 2)
    b.run_bowtie.assert_called_once_with(fastq, fastq2, bam, None, ())


def test_bowtie_sample_parameters(testdir, mock_testclass):
    sample = 'PORL2A'
    output_suffix = '-sacCer'
    bam = sample + output_suffix + '.bam'
    fastq = sample + '_1.fastq'
    fastq2 = sample + '_2.fastq'
    threads = 2
    bowtie_args = ('-x', 'sacCer3.fa',)
    b.run_bowtie = MagicMock()
    Fastq.fastq = MagicMock(side_effect=[fastq, fastq2])
    b.bowtie_sample(sample, threads, output_suffix, bowtie_args=bowtie_args)
    Fastq.fastq.assert_any_call(sample, 1)
    Fastq.fastq.assert_any_call(sample, 2)
    b.run_bowtie.assert_called_once_with(fastq, fastq2, bam, threads, bowtie_args)


def test_bowtie_sample_single(testdir, mock_testclass):
    sample = 'PORL2A'
    bam = sample + '.bam'
    fastq = sample + '_1.fastq'
    b.run_bowtie = MagicMock()
    Fastq.fastq = MagicMock(side_effect=[fastq, None])
    b.bowtie_sample(sample)
    Fastq.fastq.assert_any_call(sample, 1)
    Fastq.fastq.assert_any_call(sample, 2)
    b.run_bowtie.assert_called_once_with(fastq, None, bam, None, ())


def test_run_bowtie(testdir, mock_testclass):
    sample = 'PORL2A'
    bam = sample + '.bam'
    fastq = sample + '_1.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq)
    fastq2 = sample + '_2.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq2)
    subprocess.run = MagicMock(side_effect=create_file)
    b.run_bowtie(fastq, fastq2, bam, None, ())
    call1 = ['bowtie2', '-S', ANY, '-1', fastq, '-2', fastq2]
    call2 = ['samtools', 'view', '-b', '-o', ANY, ANY]
    call3 = ['samtools', 'sort', '-o', bam, ANY]
    subprocess.run.assert_any_call(call1, check=True)
    subprocess.run.assert_any_call(call2, check=True)
    subprocess.run.assert_any_call(call3, check=True)
    subprocess.run.assert_has_calls([call(call1, check=True), call(call2, check=True), call(call3, check=True)], True)
    assert subprocess.run.call_args_list[0].args[0][2] == subprocess.run.call_args_list[1].args[0][5]
    assert subprocess.run.call_args_list[1].args[0][4] == subprocess.run.call_args_list[2].args[0][4]


def test_run_bowtie_parameters(testdir, mock_testclass):
    sample = 'PORL2A'
    bam = sample + '.bam'
    fastq = sample + '_1.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq)
    fastq2 = sample + '_2.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq2)
    threads = 2
    bowtie_args = ('-x', 'sacCer3.fa',)
    subprocess.run = MagicMock(side_effect=create_file)
    b.run_bowtie(fastq, fastq2, bam, threads, bowtie_args)
    call1 = ['bowtie2', '-x', 'sacCer3.fa', '-p', str(threads), '-S', ANY, '-1', fastq, '-2', fastq2]
    call2 = ['samtools', 'view', '-b', '--threads', str(threads - 1), '-o', ANY, ANY]
    call3 = ['samtools', 'sort', '--threads', str(threads - 1), '-o', bam, ANY]
    subprocess.run.assert_any_call(call1, check=True)
    subprocess.run.assert_any_call(call2, check=True)
    subprocess.run.assert_any_call(call3, check=True)
    subprocess.run.assert_has_calls([call(call1, check=True), call(call2, check=True), call(call3, check=True)], True)
    assert subprocess.run.call_args_list[0].args[0][6] == subprocess.run.call_args_list[1].args[0][7]
    assert subprocess.run.call_args_list[1].args[0][6] == subprocess.run.call_args_list[2].args[0][6]


def test_run_bowtie_singlethread(testdir, mock_testclass):
    sample = 'PORL2A'
    bam = sample + '.bam'
    fastq = sample + '_1.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq)
    fastq2 = sample + '_2.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq2)
    threads = 1
    bowtie_args = ('-x', 'sacCer3.fa',)
    subprocess.run = MagicMock(side_effect=create_file)
    b.run_bowtie(fastq, fastq2, bam, threads, bowtie_args)
    call1 = ['bowtie2', '-x', 'sacCer3.fa', '-S', ANY, '-1', fastq, '-2', fastq2]
    call2 = ['samtools', 'view', '-b', '-o', ANY, ANY]
    call3 = ['samtools', 'sort', '-o', bam, ANY]
    subprocess.run.assert_any_call(call1, check=True)
    subprocess.run.assert_any_call(call2, check=True)
    subprocess.run.assert_any_call(call3, check=True)
    subprocess.run.assert_has_calls([call(call1, check=True), call(call2, check=True), call(call3, check=True)], True)
    assert subprocess.run.call_args_list[0].args[0][4] == subprocess.run.call_args_list[1].args[0][5]
    assert subprocess.run.call_args_list[1].args[0][4] == subprocess.run.call_args_list[2].args[0][4]


def test_run_bowtie_single(testdir, mock_testclass):
    sample = 'PORL2A'
    bam = sample + '.bam'
    fastq = sample + '_1.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq)
    subprocess.run = MagicMock(side_effect=create_file)
    b.run_bowtie(fastq, None, bam, None, ())
    call1 = ['bowtie2', '-S', ANY, '-U', fastq]
    call2 = ['samtools', 'view', '-b', '-o', ANY, ANY]
    call3 = ['samtools', 'sort', '-o', bam, ANY]
    subprocess.run.assert_any_call(call1, check=True)
    subprocess.run.assert_any_call(call2, check=True)
    subprocess.run.assert_any_call(call3, check=True)
    subprocess.run.assert_has_calls([call(call1, check=True), call(call2, check=True), call(call3, check=True)], True)
    assert subprocess.run.call_args_list[0].args[0][2] == subprocess.run.call_args_list[1].args[0][5]
    assert subprocess.run.call_args_list[1].args[0][4] == subprocess.run.call_args_list[2].args[0][4]


def test_run_bowtie_fastq2notexists(testdir, mock_testclass):
    sample = 'PORL2A'
    bam = sample + '.bam'
    fastq = sample + '_1.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq)
    fastq2 = sample + '_2.fastq'
    subprocess.run = MagicMock(side_effect=create_file)
    b.run_bowtie(fastq, None, bam, None, ())
    call1 = ['bowtie2', '-S', ANY, '-U', fastq]
    call2 = ['samtools', 'view', '-b', '-o', ANY, ANY]
    call3 = ['samtools', 'sort', '-o', bam, ANY]
    subprocess.run.assert_any_call(call1, check=True)
    subprocess.run.assert_any_call(call2, check=True)
    subprocess.run.assert_any_call(call3, check=True)
    subprocess.run.assert_has_calls([call(call1, check=True), call(call2, check=True), call(call3, check=True)], True)
    assert subprocess.run.call_args_list[0].args[0][2] == subprocess.run.call_args_list[1].args[0][5]
    assert subprocess.run.call_args_list[1].args[0][4] == subprocess.run.call_args_list[2].args[0][4]
