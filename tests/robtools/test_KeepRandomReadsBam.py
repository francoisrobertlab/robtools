import os.path
import shutil
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, ANY

import pysam
import pytest
from click.testing import CliRunner

from robtools import KeepRandomReadsBam
from robtools.bam import Bam


@pytest.fixture
def mock_testclass():
    keeprandomreads_samples = KeepRandomReadsBam.keeprandomreads_samples
    keeprandomreads_sample = KeepRandomReadsBam.keeprandomreads_sample
    sort = Bam.sort
    sort_by_readname = Bam.sort_by_readname
    run = subprocess.run
    yield
    KeepRandomReadsBam.keeprandomreads_samples = keeprandomreads_samples
    KeepRandomReadsBam.keeprandomreads_sample = keeprandomreads_sample
    Bam.sort = sort
    Bam.sort_by_readname = sort_by_readname
    subprocess.run = run


def create_sorted_bam(*args, **kwargs):
    sam = Path(__file__).parent.joinpath('sample-big.sam')
    output = args[1]
    cmd = ['samtools', 'view', '-h', '-b', '-o', output, sam]
    subprocess.run(cmd, check=True)


def create_unpaired_sorted_bam(*args, **kwargs):
    sam = Path(__file__).parent.joinpath('sample-big-unpaired.sam')
    output = args[1]
    cmd = ['samtools', 'view', '-h', '-b', '-o', output, sam]
    subprocess.run(cmd, check=True)


def sort_copy(*args, **kwargs):
    bam = args[0]
    output = args[1]
    shutil.copy(bam, output)


def test_keeprandomreads(mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    KeepRandomReadsBam.keeprandomreads_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(KeepRandomReadsBam.keeprandomreads_bam, ['--samples', samples])
    assert result.exit_code == 0
    KeepRandomReadsBam.keeprandomreads_samples.assert_called_once_with(samples, 10000000, True, 1, '', '-random', None)


def test_keeprandomreads_parameters(mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    count = 20000000
    threads = 4
    input_suffix = '-dedup'
    output_suffix = '-20M'
    index = 0
    KeepRandomReadsBam.keeprandomreads_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(KeepRandomReadsBam.keeprandomreads_bam,
                           ['--samples', samples, '--count', count, '--unpaired', '--threads', threads,
                            '--input-suffix', input_suffix, '--output-suffix', output_suffix, '--index', index])
    assert result.exit_code == 0
    KeepRandomReadsBam.keeprandomreads_samples.assert_called_once_with(samples, count, False, threads, input_suffix,
                                                                       output_suffix, index)


def test_keeprandomreads_samplesnotexists(mock_testclass):
    samples = 'samples.txt'
    KeepRandomReadsBam.keeprandomreads_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(KeepRandomReadsBam.keeprandomreads_bam, ['-s', samples])
    assert result.exit_code > 0
    KeepRandomReadsBam.keeprandomreads_samples.assert_not_called()


def test_keeprandomreads_samples(mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    KeepRandomReadsBam.keeprandomreads_sample = MagicMock()
    KeepRandomReadsBam.keeprandomreads_samples(samples)
    KeepRandomReadsBam.keeprandomreads_sample.assert_any_call('POLR2A', 10000000, True, None, '', '-random')
    KeepRandomReadsBam.keeprandomreads_sample.assert_any_call('ASDURF', 10000000, True, None, '', '-random')
    KeepRandomReadsBam.keeprandomreads_sample.assert_any_call('POLR1C', 10000000, True, None, '', '-random')


def test_keeprandomreads_samples_parameters(mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    count = 20000000
    paired = False
    threads = 4
    input_suffix = '-dedup'
    output_suffix = '-20M'
    index = 0
    KeepRandomReadsBam.keeprandomreads_sample = MagicMock()
    KeepRandomReadsBam.keeprandomreads_samples(samples, count, paired, threads, input_suffix, output_suffix, index)
    KeepRandomReadsBam.keeprandomreads_sample.assert_called_once_with('POLR2A', count, paired, threads, input_suffix,
                                                                      output_suffix)


def test_keeprandomreads_sample_paired(testdir, mock_testclass):
    sample = 'sample-big'
    bam = sample + '.bam'
    output = sample + '-random.bam'
    Bam.sort = MagicMock(side_effect=sort_copy)
    Bam.sort_by_readname = MagicMock(side_effect=create_sorted_bam)
    KeepRandomReadsBam.keeprandomreads_sample(sample)
    Bam.sort_by_readname.assert_any_call(bam, ANY, None)
    Bam.sort.assert_any_call(ANY, output, None)
    assert os.path.exists(output)
    with pysam.AlignmentFile(output, 'rb') as inbam:
        assert len(inbam.header.keys()) > 0
    with pysam.AlignmentFile(output, 'rb') as inbam:
        assert 1000 == inbam.count(until_eof=True)
    with pysam.AlignmentFile(output, 'rb') as inbam:
        assert 500 == inbam.count(until_eof=True, read_callback=(lambda r: r.is_read1))
    with pysam.AlignmentFile(output, 'rb') as inbam:
        assert 500 == inbam.count(until_eof=True, read_callback=(lambda r: r.is_read2))
    output_sam = output + '.sam'
    cmd = ['samtools', 'view', '-o', output_sam, output]
    subprocess.run(cmd, check=True)
    source_sam = Path(__file__).parent.joinpath('sample-big.sam')
    with open(source_sam, 'r') as source, open(output_sam, 'r') as outsam:
        expected_lines = source.readlines()
        for out_line in outsam:
            assert out_line in expected_lines


def test_keeprandomreads_sample_paired_parameters(testdir, mock_testclass):
    sample = 'sample'
    count = 200
    threads = 4
    input_suffix = '-big'
    output_suffix = '-200'
    bam = sample + input_suffix + '.bam'
    output = sample + output_suffix + '.bam'
    Bam.sort = MagicMock(side_effect=sort_copy)
    Bam.sort_by_readname = MagicMock(side_effect=create_sorted_bam)
    KeepRandomReadsBam.keeprandomreads_sample(sample, count, True, threads, input_suffix, output_suffix)
    Bam.sort_by_readname.assert_any_call(bam, ANY, threads)
    Bam.sort.assert_any_call(ANY, output, threads)
    assert os.path.exists(output)
    with pysam.AlignmentFile(output, 'rb') as inbam:
        assert len(inbam.header.keys()) > 0
    with pysam.AlignmentFile(output, 'rb') as inbam:
        assert count * 2 == inbam.count(until_eof=True)
    with pysam.AlignmentFile(output, 'rb') as inbam:
        assert count == inbam.count(until_eof=True, read_callback=(lambda r: r.is_read1))
    with pysam.AlignmentFile(output, 'rb') as inbam:
        assert count == inbam.count(until_eof=True, read_callback=(lambda r: r.is_read2))
    output_sam = os.path.join(str(testdir), os.path.basename(output) + '.sam')
    cmd = ['samtools', 'view', '-o', output_sam, output]
    subprocess.run(cmd, check=True)
    source_sam = Path(__file__).parent.joinpath('sample-big.sam')
    with open(source_sam, 'r') as source, open(output_sam, 'r') as outsam:
        expected_lines = source.readlines()
        i = 0
        for out_line in outsam:
            if i % 2 == 0:
                assert out_line in expected_lines
                line_index = expected_lines.index(out_line)
            else:
                assert out_line == expected_lines[line_index + 1]
            i = i + 1


def test_keeprandomreads_sample_unpaired(testdir, mock_testclass):
    sample = 'sample-big-unpaired'
    bam = sample + '.bam'
    output = sample + '-random.bam'
    Bam.sort = MagicMock(side_effect=sort_copy)
    Bam.sort_by_readname = MagicMock(side_effect=create_unpaired_sorted_bam)
    KeepRandomReadsBam.keeprandomreads_sample(sample, paired=False)
    Bam.sort_by_readname.assert_any_call(bam, ANY, None)
    Bam.sort.assert_any_call(ANY, output, None)
    assert os.path.exists(output)
    with pysam.AlignmentFile(output, 'rb') as inbam:
        assert len(inbam.header.keys()) > 0
    with pysam.AlignmentFile(output, 'rb') as inbam:
        assert 803 == inbam.count(until_eof=True)
    output_sam = os.path.join(str(testdir), os.path.basename(output) + '.sam')
    cmd = ['samtools', 'view', '-o', output_sam, output]
    subprocess.run(cmd, check=True)
    source_sam = Path(__file__).parent.joinpath('sample-big-unpaired.sam')
    with open(source_sam, 'r') as source, open(output_sam, 'r') as outsam:
        expected_lines = source.readlines()
        for out_line in outsam:
            assert out_line in expected_lines


def test_keeprandomreads_sample_unpaired_parameters(testdir, mock_testclass):
    sample = 'sample-big'
    count = 200
    threads = 4
    input_suffix = '-unpaired'
    output_suffix = '-unpaired-200'
    bam = sample + input_suffix + '.bam'
    output = sample + output_suffix + '.bam'
    Bam.sort = MagicMock(side_effect=sort_copy)
    Bam.sort_by_readname = MagicMock(side_effect=create_unpaired_sorted_bam)
    KeepRandomReadsBam.keeprandomreads_sample(sample, count, False, threads, input_suffix, output_suffix)
    Bam.sort_by_readname.assert_any_call(bam, ANY, threads)
    Bam.sort.assert_any_call(ANY, output, threads)
    assert os.path.exists(output)
    with pysam.AlignmentFile(output, 'rb') as inbam:
        assert len(inbam.header.keys()) > 0
    with pysam.AlignmentFile(output, 'rb') as inbam:
        assert count == inbam.count(until_eof=True)
    output_sam = os.path.join(str(testdir), os.path.basename(output) + '.sam')
    cmd = ['samtools', 'view', '-o', output_sam, output]
    subprocess.run(cmd, check=True)
    source_sam = Path(__file__).parent.joinpath('sample-big-unpaired.sam')
    with open(source_sam, 'r') as source, open(output_sam, 'r') as outsam:
        expected_lines = source.readlines()
        for out_line in outsam:
            assert out_line in expected_lines
