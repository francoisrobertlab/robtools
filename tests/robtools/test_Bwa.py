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

from robtools import Bwa as b
from robtools.seq import Fastq


@pytest.fixture
def mock_testclass():
    bwa_samples = b.bwa_samples
    bwa_sample = b.bwa_sample
    run_bwa = b.run_bwa
    fastq = Fastq.fastq
    run = subprocess.run
    yield
    b.bwa_samples = bwa_samples
    b.bwa_sample = bwa_sample
    b.run_bwa = run_bwa
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


def test_bwa(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    fasta = Path(__file__).parent.joinpath('sacCer3.fa')
    b.bwa_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(b.bwa, ['--samples', samples, '--fasta', fasta])
    assert result.exit_code == 0
    b.bwa_samples.assert_called_once_with(samples, fasta, 1, '', None, ())


def test_bwa_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    fasta = Path(__file__).parent.joinpath('sacCer3.fa')
    threads = 2
    output_suffix = '-sacCer'
    index = 1
    b.bwa_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(b.bwa, ['--samples', samples, '--fasta', fasta, '-x', 'sacCer3.fa', '--threads', threads, '--output-suffix', output_suffix, '--index', index])
    assert result.exit_code == 0
    b.bwa_samples.assert_called_once_with(samples, fasta, threads, output_suffix, index, ('-x', 'sacCer3.fa',))


def test_bwa_samplesnotexists(testdir, mock_testclass):
    samples = 'samples.txt'
    fasta = Path(__file__).parent.joinpath('sacCer3.fa')
    b.bwa_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(b.bwa, ['--samples', samples, '--fasta', fasta])
    assert result.exit_code != 0
    b.bwa_samples.assert_not_called()


def test_bwa_fastanotexists(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    fasta = 'sacCer3.fa'
    b.bwa_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(b.bwa, ['--samples', samples, '--fasta', fasta])
    assert result.exit_code != 0
    b.bwa_samples.assert_not_called()


def test_bwa_samples(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    fasta = Path(__file__).parent.joinpath('sacCer3.fa')
    b.bwa_sample = MagicMock()
    b.bwa_samples(samples, fasta)
    b.bwa_sample.assert_any_call('POLR2A', fasta, None, '', ())
    b.bwa_sample.assert_any_call('ASDURF', fasta, None, '', ())
    b.bwa_sample.assert_any_call('POLR1C', fasta, None, '', ())


def test_bwa_samples_second(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    fasta = Path(__file__).parent.joinpath('sacCer3.fa')
    b.bwa_sample = MagicMock()
    b.bwa_samples(samples, fasta, index=1)
    b.bwa_sample.assert_called_once_with('ASDURF', fasta, None, '', ())


def test_bwa_samples_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    fasta = Path(__file__).parent.joinpath('sacCer3.fa')
    threads = 2
    output_suffix = '-sacCer'
    bwa_args = ('-x', 'sacCer3.fa',)
    b.bwa_sample = MagicMock()
    b.bwa_samples(samples, fasta, threads, output_suffix, bwa_args=bwa_args)
    b.bwa_sample.assert_any_call('POLR2A', fasta, threads, output_suffix, bwa_args)
    b.bwa_sample.assert_any_call('ASDURF', fasta, threads, output_suffix, bwa_args)
    b.bwa_sample.assert_any_call('POLR1C', fasta, threads, output_suffix, bwa_args)


def test_bwa_sample(testdir, mock_testclass):
    sample = 'PORL2A'
    fasta = 'sacCer3.fa'
    bam = sample + '.bam'
    fastq = sample + '_1.fastq'
    fastq2 = sample + '_2.fastq'
    b.run_bwa = MagicMock()
    Fastq.fastq = MagicMock(side_effect=[fastq, fastq2])
    b.bwa_sample(sample, fasta)
    Fastq.fastq.assert_any_call(sample, 1)
    Fastq.fastq.assert_any_call(sample, 2)
    b.run_bwa.assert_called_once_with(fastq, fastq2, fasta, bam, None, ())


def test_bwa_sample_parameters(testdir, mock_testclass):
    sample = 'PORL2A'
    fasta = 'sacCer3.fa'
    output_suffix = '-sacCer'
    bam = sample + output_suffix + '.bam'
    fastq = sample + '_1.fastq'
    fastq2 = sample + '_2.fastq'
    threads = 2
    bwa_args = ('-x', 'sacCer3.fa',)
    b.run_bwa = MagicMock()
    Fastq.fastq = MagicMock(side_effect=[fastq, fastq2])
    b.bwa_sample(sample, fasta, threads, output_suffix, bwa_args=bwa_args)
    Fastq.fastq.assert_any_call(sample, 1)
    Fastq.fastq.assert_any_call(sample, 2)
    b.run_bwa.assert_called_once_with(fastq, fastq2, fasta, bam, threads, bwa_args)


def test_bwa_sample_single(testdir, mock_testclass):
    sample = 'PORL2A'
    fasta = 'sacCer3.fa'
    bam = sample + '.bam'
    fastq = sample + '_1.fastq'
    b.run_bwa = MagicMock()
    Fastq.fastq = MagicMock(side_effect=[fastq, None])
    b.bwa_sample(sample, fasta)
    Fastq.fastq.assert_any_call(sample, 1)
    Fastq.fastq.assert_any_call(sample, 2)
    b.run_bwa.assert_called_once_with(fastq, None, fasta, bam, None, ())


def test_bwa_index(testdir, mock_testclass):
    fasta = 'sacCer3.fa'
    subprocess.run = MagicMock(side_effect=create_file)
    b.bwa_index(fasta)
    subprocess.run.assert_called_once_with(['bwa', 'index', fasta], check=True)


def test_run_bwa(testdir, mock_testclass):
    sample = 'PORL2A'
    fasta = 'sacCer3.fa'
    bam = sample + '.bam'
    fastq = sample + '_1.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq)
    fastq2 = sample + '_2.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq2)
    subprocess.run = MagicMock(side_effect=create_file)
    b.run_bwa(fastq, fastq2, fasta, bam, None, ())
    call1 = ['bwa', 'mem', '-o', ANY, fasta, fastq, fastq2]
    call2 = ['samtools', 'view', '-b', '-o', ANY, ANY]
    call3 = ['samtools', 'sort', '-o', bam, ANY]
    subprocess.run.assert_any_call(call1, check=True)
    subprocess.run.assert_any_call(call2, check=True)
    subprocess.run.assert_any_call(call3, check=True)
    subprocess.run.assert_has_calls([call(call1, check=True), call(call2, check=True), call(call3, check=True)], True)
    assert subprocess.run.call_args_list[0].args[0][3] == subprocess.run.call_args_list[1].args[0][5]
    assert subprocess.run.call_args_list[1].args[0][4] == subprocess.run.call_args_list[2].args[0][4]


def test_run_bwa_parameters(testdir, mock_testclass):
    sample = 'PORL2A'
    fasta = 'sacCer3.fa'
    bam = sample + '.bam'
    fastq = sample + '_1.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq)
    fastq2 = sample + '_2.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq2)
    threads = 2
    bwa_args = ('-x', 'sacCer3.fa',)
    subprocess.run = MagicMock(side_effect=create_file)
    b.run_bwa(fastq, fastq2, fasta, bam, threads, bwa_args)
    call1 = ['bwa', 'mem', '-x', 'sacCer3.fa', '-t', str(threads), '-o', ANY, fasta, fastq, fastq2]
    call2 = ['samtools', 'view', '-b', '--threads', str(threads - 1), '-o', ANY, ANY]
    call3 = ['samtools', 'sort', '--threads', str(threads - 1), '-o', bam, ANY]
    subprocess.run.assert_any_call(call1, check=True)
    subprocess.run.assert_any_call(call2, check=True)
    subprocess.run.assert_any_call(call3, check=True)
    subprocess.run.assert_has_calls([call(call1, check=True), call(call2, check=True), call(call3, check=True)], True)
    assert subprocess.run.call_args_list[0].args[0][7] == subprocess.run.call_args_list[1].args[0][7]
    assert subprocess.run.call_args_list[1].args[0][6] == subprocess.run.call_args_list[2].args[0][6]


def test_run_bwa_singlethread(testdir, mock_testclass):
    sample = 'PORL2A'
    fasta = 'sacCer3.fa'
    bam = sample + '.bam'
    fastq = sample + '_1.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq)
    fastq2 = sample + '_2.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq2)
    threads = 1
    bwa_args = ('-x', 'sacCer3.fa',)
    subprocess.run = MagicMock(side_effect=create_file)
    b.run_bwa(fastq, fastq2, fasta, bam, threads, bwa_args)
    call1 = ['bwa', 'mem', '-x', 'sacCer3.fa', '-o', ANY, fasta, fastq, fastq2]
    call2 = ['samtools', 'view', '-b', '-o', ANY, ANY]
    call3 = ['samtools', 'sort', '-o', bam, ANY]
    subprocess.run.assert_any_call(call1, check=True)
    subprocess.run.assert_any_call(call2, check=True)
    subprocess.run.assert_any_call(call3, check=True)
    subprocess.run.assert_has_calls([call(call1, check=True), call(call2, check=True), call(call3, check=True)], True)
    assert subprocess.run.call_args_list[0].args[0][5] == subprocess.run.call_args_list[1].args[0][5]
    assert subprocess.run.call_args_list[1].args[0][4] == subprocess.run.call_args_list[2].args[0][4]


def test_run_bwa_single(testdir, mock_testclass):
    sample = 'PORL2A'
    fasta = 'sacCer3.fa'
    bam = sample + '.bam'
    fastq = sample + '_1.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq)
    subprocess.run = MagicMock(side_effect=create_file)
    b.run_bwa(fastq, None, fasta, bam, None, ())
    call1 = ['bwa', 'mem', '-o', ANY, fasta, fastq]
    call2 = ['samtools', 'view', '-b', '-o', ANY, ANY]
    call3 = ['samtools', 'sort', '-o', bam, ANY]
    subprocess.run.assert_any_call(call1, check=True)
    subprocess.run.assert_any_call(call2, check=True)
    subprocess.run.assert_any_call(call3, check=True)
    subprocess.run.assert_has_calls([call(call1, check=True), call(call2, check=True), call(call3, check=True)], True)
    assert subprocess.run.call_args_list[0].args[0][3] == subprocess.run.call_args_list[1].args[0][5]
    assert subprocess.run.call_args_list[1].args[0][4] == subprocess.run.call_args_list[2].args[0][4]


def test_run_bwa_fastq2notexists(testdir, mock_testclass):
    sample = 'PORL2A'
    fasta = 'sacCer3.fa'
    bam = sample + '.bam'
    fastq = sample + '_1.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq)
    fastq2 = sample + '_2.fastq'
    subprocess.run = MagicMock(side_effect=create_file)
    b.run_bwa(fastq, None, fasta, bam, None, ())
    call1 = ['bwa', 'mem', '-o', ANY, fasta, fastq]
    call2 = ['samtools', 'view', '-b', '-o', ANY, ANY]
    call3 = ['samtools', 'sort', '-o', bam, ANY]
    subprocess.run.assert_any_call(call1, check=True)
    subprocess.run.assert_any_call(call2, check=True)
    subprocess.run.assert_any_call(call3, check=True)
    subprocess.run.assert_has_calls([call(call1, check=True), call(call2, check=True), call(call3, check=True)], True)
    assert subprocess.run.call_args_list[0].args[0][3] == subprocess.run.call_args_list[1].args[0][5]
    assert subprocess.run.call_args_list[1].args[0][4] == subprocess.run.call_args_list[2].args[0][4]
