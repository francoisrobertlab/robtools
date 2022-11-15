import gzip
import os.path
import re
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from robtools import KeepRandomReads


@pytest.fixture
def mock_testclass():
    keeprandomreads_samples = KeepRandomReads.keeprandomreads_samples
    keeprandomreads_sample = KeepRandomReads.keeprandomreads_sample
    yield
    KeepRandomReads.keeprandomreads_samples = keeprandomreads_samples
    KeepRandomReads.keeprandomreads_sample = keeprandomreads_sample


def test_keeprandomreads(mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    KeepRandomReads.keeprandomreads_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(KeepRandomReads.keeprandomreads, ['--samples', samples])
    assert result.exit_code == 0
    KeepRandomReads.keeprandomreads_samples.assert_called_once_with(samples, 10000000, True, '', '-random', None)


def test_keeprandomreads_parameters(mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    count = 20000000
    input_suffix = '-dedup'
    output_suffix = '-20M'
    index = 0
    KeepRandomReads.keeprandomreads_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(KeepRandomReads.keeprandomreads,
                           ['--samples', samples, '--count', count, '--unpaired', '--input-suffix', input_suffix,
                            '--output-suffix', output_suffix, '--index', index])
    assert result.exit_code == 0
    KeepRandomReads.keeprandomreads_samples.assert_called_once_with(samples, count, False, input_suffix, output_suffix,
                                                                    index)


def test_keeprandomreads_samplesnotexists(mock_testclass):
    samples = 'samples.txt'
    KeepRandomReads.keeprandomreads_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(KeepRandomReads.keeprandomreads, ['-s', samples])
    assert result.exit_code > 0
    KeepRandomReads.keeprandomreads_samples.assert_not_called()


def test_keeprandomreads_samples(mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    KeepRandomReads.keeprandomreads_sample = MagicMock()
    KeepRandomReads.keeprandomreads_samples(samples)
    KeepRandomReads.keeprandomreads_sample.assert_any_call('POLR2A', 10000000, True, '', '-random')
    KeepRandomReads.keeprandomreads_sample.assert_any_call('ASDURF', 10000000, True, '', '-random')
    KeepRandomReads.keeprandomreads_sample.assert_any_call('POLR1C', 10000000, True, '', '-random')


def test_keeprandomreads_samples_parameters(mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    count = 20000000
    paired = False
    threads = 4
    input_suffix = '-dedup'
    output_suffix = '-20M'
    index = 0
    KeepRandomReads.keeprandomreads_sample = MagicMock()
    KeepRandomReads.keeprandomreads_samples(samples, count, paired, input_suffix, output_suffix, index)
    KeepRandomReads.keeprandomreads_sample.assert_called_once_with('POLR2A', count, paired, input_suffix, output_suffix)


def test_keeprandomreads_sample_paired(testdir, mock_testclass):
    sample = 'sample'
    fastq1 = sample + '_R1.fastq.gz'
    with open(Path(__file__).parent.joinpath('sample_R1.fastq')) as fastq_in:
        fastq1_lines = fastq_in.readlines()
    with gzip.open(fastq1, 'wt') as zip_out:
        for line in fastq1_lines:
            zip_out.write(line)
    fastq2 = sample + '_R2.fastq.gz'
    with open(Path(__file__).parent.joinpath('sample_R2.fastq')) as fastq_in:
        fastq2_lines = fastq_in.readlines()
    with gzip.open(fastq2, 'wt') as zip_out:
        for line in fastq2_lines:
            zip_out.write(line)
    output1 = sample + '-random_R1.fastq.gz'
    output2 = sample + '-random_R2.fastq.gz'
    KeepRandomReads.keeprandomreads_sample(sample)
    assert os.path.exists(output1)
    assert os.path.exists(output2)
    with gzip.open(output1, 'rt') as output1_out:
        output1_lines = output1_out.readlines()
    with gzip.open(output2, 'rt') as output2_out:
        output2_lines = output2_out.readlines()
    assert len(output1_lines) == len(output2_lines)
    assert len(output1_lines) == len(fastq1_lines)
    for i in range(0, len(output1_lines)):
        if output1_lines[0].startswith('@'):
            assert re.split('\\s', output1_lines[0])[0] == re.split('\\s', output2_lines[0])[0]
    for line in output1_lines:
        assert line in fastq1_lines
    for line in output2_lines:
        assert line in fastq2_lines


def test_keeprandomreads_sample_paired_parameters(testdir, mock_testclass):
    sample = 'sample'
    count = 10
    input_suffix = '-in'
    output_suffix = '-out'
    fastq1 = sample + input_suffix + '_R1.fastq.gz'
    with open(Path(__file__).parent.joinpath('sample_R1.fastq')) as fastq_in:
        fastq1_lines = fastq_in.readlines()
    with gzip.open(fastq1, 'wt') as zip_out:
        for line in fastq1_lines:
            zip_out.write(line)
    fastq2 = sample + input_suffix + '_R2.fastq.gz'
    with open(Path(__file__).parent.joinpath('sample_R2.fastq')) as fastq_in:
        fastq2_lines = fastq_in.readlines()
    with gzip.open(fastq2, 'wt') as zip_out:
        for line in fastq2_lines:
            zip_out.write(line)
    output1 = sample + output_suffix + '_R1.fastq.gz'
    output2 = sample + output_suffix + '_R2.fastq.gz'
    KeepRandomReads.keeprandomreads_sample(sample, count, True, input_suffix, output_suffix)
    assert os.path.exists(output1)
    assert os.path.exists(output2)
    with gzip.open(output1, 'rt') as output1_out:
        output1_lines = output1_out.readlines()
    with gzip.open(output2, 'rt') as output2_out:
        output2_lines = output2_out.readlines()
    assert len(output1_lines) == len(output2_lines)
    assert count * 4 == len(output1_lines)
    for i in range(0, len(output1_lines)):
        if output1_lines[0].startswith('@'):
            assert re.split('\\s', output1_lines[0])[0] == re.split('\\s', output2_lines[0])[0]
    for line in output1_lines:
        assert line in fastq1_lines
    for line in output2_lines:
        assert line in fastq2_lines


def test_keeprandomreads_sample_paired_wrong_second(testdir, mock_testclass):
    sample = 'sample'
    fastq1 = sample + '_R1.fastq.gz'
    with open(Path(__file__).parent.joinpath('sample_R1.fastq')) as fastq_in:
        fastq1_lines = fastq_in.readlines()
    with gzip.open(fastq1, 'wt') as zip_out:
        for line in fastq1_lines:
            zip_out.write(line)
    fastq2 = sample + '_R2.fastq.gz'
    with open(Path(__file__).parent.joinpath('sample_R2.fastq')) as fastq_in:
        fastq2_lines = fastq_in.readlines()
    fastq2_lines[4] = '@B' + fastq2_lines[4][2:]
    with gzip.open(fastq2, 'wt') as zip_out:
        for line in fastq2_lines:
            zip_out.write(line)
    output1 = sample + '-random_R1.fastq.gz'
    output2 = sample + '-random_R2.fastq.gz'
    with pytest.raises(AssertionError) as assert_error:
        KeepRandomReads.keeprandomreads_sample(sample)
    assert assert_error


def test_keeprandomreads_sample_unpaired(testdir, mock_testclass):
    sample = 'sample'
    fastq1 = sample + '_R1.fastq.gz'
    with open(Path(__file__).parent.joinpath('sample_R1.fastq')) as fastq_in:
        fastq1_lines = fastq_in.readlines()
    with gzip.open(fastq1, 'wt') as zip_out:
        for line in fastq1_lines:
            zip_out.write(line)
    output1 = sample + '-random_R1.fastq.gz'
    output2 = sample + '-random_R2.fastq.gz'
    KeepRandomReads.keeprandomreads_sample(sample, paired=False)
    assert os.path.exists(output1)
    assert not os.path.exists(output2)
    with gzip.open(output1, 'rt') as output1_out:
        output1_lines = output1_out.readlines()
    assert 100 == len(output1_lines)
    for line in output1_lines:
        assert line in fastq1_lines


def test_keeprandomreads_sample_unpaired_parameters(testdir, mock_testclass):
    sample = 'sample'
    count = 10
    input_suffix = '-in'
    output_suffix = '-out'
    fastq1 = sample + input_suffix + '_R1.fastq.gz'
    with open(Path(__file__).parent.joinpath('sample_R1.fastq')) as fastq_in:
        fastq1_lines = fastq_in.readlines()
    with gzip.open(fastq1, 'wt') as zip_out:
        for line in fastq1_lines:
            zip_out.write(line)
    output1 = sample + output_suffix + '_R1.fastq.gz'
    output2 = sample + output_suffix + '_R2.fastq.gz'
    KeepRandomReads.keeprandomreads_sample(sample, count, False, input_suffix, output_suffix)
    assert os.path.exists(output1)
    assert not os.path.exists(output2)
    with gzip.open(output1, 'rt') as output1_out:
        output1_lines = output1_out.readlines()
    assert count * 4 == len(output1_lines)
    for line in output1_lines:
        assert line in fastq1_lines
