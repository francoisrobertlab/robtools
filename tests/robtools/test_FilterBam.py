import logging
import os
from pathlib import Path
import subprocess
from unittest.mock import MagicMock, ANY

import click
from click.testing import CliRunner
import pytest

from robtools import FilterBam as fb


@pytest.fixture
def mock_testclass():
    filter_bam = fb.filter_bam
    filter_bam_sample = fb.filter_bam_sample
    filter_mapped = fb.filter_mapped
    remove_duplicates = fb.remove_duplicates
    sort = fb.sort
    run = subprocess.run
    yield
    fb.filter_bam = filter_bam
    fb.filter_bam_sample = filter_bam_sample
    fb.filter_mapped = filter_mapped
    fb.remove_duplicates = remove_duplicates
    fb.sort = sort
    subprocess.run = run
    
    
def create_file(*args, **kwargs):
    if 'stdout' in kwargs:
        outfile = kwargs['stdout']
        outfile.write('test')
    elif '-o' in args[0]:
        output = args[0][args[0].index('-o') + 1]
        with open(output, 'w') as outfile:
            outfile.write('test')


def create_file_fixmate(*args, **kwargs):
    output = args[lenght(args - 1)]
    with open(output, 'w') as outfile:
        outfile.write('test')


def create_file_markdup(*args, **kwargs):
    output = args[lenght(args - 1)]
    with open(output, 'w') as outfile:
        outfile.write('test')


def test_filterbam(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    threads = 1
    fb.filter_bam = MagicMock()
    runner = CliRunner()
    result = runner.invoke(fb.filterbam, ['-s', samples])
    assert result.exit_code == 0
    fb.filter_bam.assert_called_once_with(samples, True, True, None, threads, '', '', None)


def test_filterbam_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    quality = 20
    threads = 2
    input_suffix = '-i-sacCer'
    output_suffix = '-sacCer'
    index = 1
    fb.filter_bam = MagicMock()
    runner = CliRunner()
    result = runner.invoke(fb.filterbam, ['-s', samples, '--unpaired', '--no-dedup', '-q', quality, '--threads', threads, '--input-suffix', input_suffix, '--output-suffix', output_suffix, '--index', index])
    assert result.exit_code == 0
    fb.filter_bam.assert_called_once_with(samples, False, False, quality, threads, input_suffix, output_suffix, index)


def test_filter_bam(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    fb.filter_bam_sample = MagicMock()
    fb.filter_bam(samples)
    fb.filter_bam_sample.assert_any_call('POLR2A', True, True, None, None, '', '')
    fb.filter_bam_sample.assert_any_call('ASDURF', True, True, None, None, '', '')
    fb.filter_bam_sample.assert_any_call('POLR1C', True, True, None, None, '', '')


def test_filter_bam_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    quality = 20
    threads = 2
    input_suffix = '-i-sacCer'
    output_suffix = '-sacCer'
    fb.filter_bam_sample = MagicMock()
    fb.filter_bam(samples, False, False, quality, threads, input_suffix, output_suffix)
    fb.filter_bam_sample.assert_any_call('POLR2A', False, False, quality, threads, input_suffix, output_suffix)
    fb.filter_bam_sample.assert_any_call('ASDURF', False, False, quality, threads, input_suffix, output_suffix)
    fb.filter_bam_sample.assert_any_call('POLR1C', False, False, quality, threads, input_suffix, output_suffix)


def test_filter_bam_second(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    threads = 2
    fb.filter_bam_sample = MagicMock()
    fb.filter_bam(samples, False, True, threads=threads, index=1)
    fb.filter_bam_sample.assert_called_once_with('ASDURF', False, True, None, threads, '', '')


def test_filter_bam_sample_single(testdir, mock_testclass):
    sample = 'POLR2A'
    bam = sample + '.bam'
    bam_filtered = sample + '-filtered.bam'
    bam_dedup = sample + '-dedup.bam'
    fb.filter_mapped = MagicMock(create_file(['-o', bam_filtered]))
    fb.remove_duplicates = MagicMock(create_file(['-o', bam_dedup]))
    fb.filter_bam_sample(sample, False, True)
    fb.filter_mapped.assert_called_with(bam, bam_filtered, False, None, None)
    fb.remove_duplicates.assert_called_with(bam_filtered, bam_dedup, None)
    assert os.path.exists(bam_filtered)
    assert os.path.exists(bam_dedup)


def test_filter_bam_sample_single_nodedup(testdir, mock_testclass):
    sample = 'POLR2A'
    bam = sample + '.bam'
    bam_filtered = sample + '-filtered.bam'
    bam_dedup = sample + '-dedup.bam'
    fb.filter_mapped = MagicMock(create_file(['-o', bam_filtered]))
    fb.remove_duplicates = MagicMock()
    fb.filter_bam_sample(sample, False, False)
    fb.filter_mapped.assert_called_with(bam, bam_filtered, False, None, None)
    fb.remove_duplicates.assert_not_called()
    assert os.path.exists(bam_filtered)
    assert not os.path.exists(bam_dedup)


def test_filter_bam_sample_single_parameters(testdir, mock_testclass):
    sample = 'POLR2A'
    input_suffix = '-i-sacCer'
    output_suffix = '-sacCer'
    bam = sample + input_suffix + '.bam'
    bam_filtered = sample + output_suffix + '-filtered.bam'
    bam_dedup = sample + output_suffix + '-dedup.bam'
    quality = 20
    threads = 3
    fb.filter_mapped = MagicMock(create_file(['-o', bam_filtered]))
    fb.remove_duplicates = MagicMock(create_file(['-o', bam_dedup]))
    fb.filter_bam_sample(sample, False, True, quality, threads, input_suffix, output_suffix)
    fb.filter_mapped.assert_called_with(bam, bam_filtered, False, quality, threads)
    fb.remove_duplicates.assert_called_with(bam_filtered, bam_dedup, threads)
    assert os.path.exists(bam_filtered)
    assert os.path.exists(bam_dedup)


def test_filter_bam_sample_paired(testdir, mock_testclass):
    sample = 'POLR2A'
    bam = sample + '.bam'
    bam_filtered = sample + '-filtered.bam'
    bam_dedup = sample + '-dedup.bam'
    fb.filter_mapped = MagicMock(create_file(['-o', bam_filtered]))
    fb.remove_duplicates = MagicMock(create_file(['-o', bam_dedup]))
    fb.filter_bam_sample(sample, True, True)
    fb.filter_mapped.assert_called_with(bam, bam_filtered, True, None, None)
    fb.remove_duplicates.assert_called_with(bam_filtered, bam_dedup, None)
    assert os.path.exists(bam_filtered)
    assert os.path.exists(bam_dedup)


def test_filter_bam_sample_paired_nodedup(testdir, mock_testclass):
    sample = 'POLR2A'
    bam = sample + '.bam'
    bam_filtered = sample + '-filtered.bam'
    bam_dedup = sample + '-dedup.bam'
    fb.filter_mapped = MagicMock(create_file(['-o', bam_filtered]))
    fb.remove_duplicates = MagicMock()
    fb.filter_bam_sample(sample, True, False)
    fb.filter_mapped.assert_called_with(bam, bam_filtered, True, None, None)
    fb.remove_duplicates.assert_not_called()
    assert os.path.exists(bam_filtered)
    assert not os.path.exists(bam_dedup)


def test_filter_bam_sample_paired_parameters(testdir, mock_testclass):
    sample = 'POLR2A'
    input_suffix = '-i-sacCer'
    output_suffix = '-sacCer'
    bam = sample + input_suffix + '.bam'
    bam_filtered = sample + output_suffix + '-filtered.bam'
    bam_dedup = sample + output_suffix + '-dedup.bam'
    quality = 20
    threads = 3
    fb.filter_mapped = MagicMock(create_file(['-o', bam_filtered]))
    fb.remove_duplicates = MagicMock(create_file(['-o', bam_dedup]))
    fb.filter_bam_sample(sample, True, True, quality, threads, input_suffix, output_suffix)
    fb.filter_mapped.assert_called_with(bam, bam_filtered, True, quality, threads)
    fb.remove_duplicates.assert_called_with(bam_filtered, bam_dedup, threads)
    assert os.path.exists(bam_filtered)
    assert os.path.exists(bam_dedup)


def test_filter_mapped_single(testdir, mock_testclass):
    bam = 'POLR2A.bam'
    output = 'POLR2A-out.bam'
    subprocess.run = MagicMock(side_effect=create_file)
    fb.filter_mapped(bam, output, False)
    subprocess.run.assert_any_call(['samtools', 'view', '-b', '-F', '2048', '-F', '256', '-F', '4', '-o', ANY, bam], check=True)
    subprocess.run.assert_any_call(['samtools', 'sort', '-o', output, ANY], check=True)
    assert subprocess.run.call_args_list[0].args[0][10] == subprocess.run.call_args_list[1].args[0][4]


def test_filter_mapped_single_quality(testdir, mock_testclass):
    bam = 'POLR2A.bam'
    output = 'POLR2A-out.bam'
    quality = 20
    subprocess.run = MagicMock(side_effect=create_file)
    fb.filter_mapped(bam, output, False, quality=quality)
    subprocess.run.assert_any_call(['samtools', 'view', '-b', '-F', '2048', '-F', '256', '-F', '4', '-q', str(quality), '-o', ANY, bam], check=True)
    subprocess.run.assert_any_call(['samtools', 'sort', '-o', output, ANY], check=True)
    assert subprocess.run.call_args_list[0].args[0][12] == subprocess.run.call_args_list[1].args[0][4]


def test_filter_mapped_single_threads(testdir, mock_testclass):
    bam = 'POLR2A.bam'
    output = 'POLR2A-out.bam'
    threads = 3
    subprocess.run = MagicMock(side_effect=create_file)
    fb.filter_mapped(bam, output, False, threads=threads)
    subprocess.run.assert_any_call(['samtools', 'view', '-b', '-F', '2048', '-F', '256', '-F', '4', '--threads', str(threads - 1), '-o', ANY, bam], check=True)
    subprocess.run.assert_any_call(['samtools', 'sort', '--threads', str(threads - 1), '-o', output, ANY], check=True)
    assert subprocess.run.call_args_list[0].args[0][12] == subprocess.run.call_args_list[1].args[0][6]


def test_filter_mapped_single_qualitythreads(testdir, mock_testclass):
    bam = 'POLR2A.bam'
    output = 'POLR2A-out.bam'
    quality = 20
    threads = 3
    subprocess.run = MagicMock(side_effect=create_file)
    fb.filter_mapped(bam, output, False, quality=quality, threads=threads)
    subprocess.run.assert_any_call(['samtools', 'view', '-b', '-F', '2048', '-F', '256', '-F', '4', '-q', str(quality), '--threads', str(threads - 1), '-o', ANY, bam], check=True)
    subprocess.run.assert_any_call(['samtools', 'sort', '--threads', str(threads - 1), '-o', output, ANY], check=True)
    assert subprocess.run.call_args_list[0].args[0][14] == subprocess.run.call_args_list[1].args[0][6]


def test_filter_mapped_single_singlethread(testdir, mock_testclass):
    bam = 'POLR2A.bam'
    output = 'POLR2A-out.bam'
    threads = 1
    subprocess.run = MagicMock(side_effect=create_file)
    fb.filter_mapped(bam, output, False, threads=threads)
    subprocess.run.assert_any_call(['samtools', 'view', '-b', '-F', '2048', '-F', '256', '-F', '4', '-o', ANY, bam], check=True)
    subprocess.run.assert_any_call(['samtools', 'sort', '-o', output, ANY], check=True)
    assert subprocess.run.call_args_list[0].args[0][10] == subprocess.run.call_args_list[1].args[0][4]


def test_filter_mapped_paired(testdir, mock_testclass):
    bam = 'POLR2A.bam'
    output = 'POLR2A-out.bam'
    subprocess.run = MagicMock(side_effect=create_file)
    fb.filter_mapped(bam, output, True)
    subprocess.run.assert_any_call(['samtools', 'view', '-b', '-F', '2048', '-F', '256', '-f', '2', '-o', ANY, bam], check=True)
    subprocess.run.assert_any_call(['samtools', 'sort', '-o', output, ANY], check=True)
    assert subprocess.run.call_args_list[0].args[0][10] == subprocess.run.call_args_list[1].args[0][4]


def test_filter_mapped_paired_quality(testdir, mock_testclass):
    bam = 'POLR2A.bam'
    output = 'POLR2A-out.bam'
    quality = 20
    subprocess.run = MagicMock(side_effect=create_file)
    fb.filter_mapped(bam, output, True, quality=quality)
    subprocess.run.assert_any_call(['samtools', 'view', '-b', '-F', '2048', '-F', '256', '-f', '2', '-q', str(quality), '-o', ANY, bam], check=True)
    subprocess.run.assert_any_call(['samtools', 'sort', '-o', output, ANY], check=True)
    assert subprocess.run.call_args_list[0].args[0][12] == subprocess.run.call_args_list[1].args[0][4]


def test_filter_mapped_paired_threads(testdir, mock_testclass):
    bam = 'POLR2A.bam'
    output = 'POLR2A-out.bam'
    threads = 3
    subprocess.run = MagicMock(side_effect=create_file)
    fb.filter_mapped(bam, output, True, threads=threads)
    subprocess.run.assert_any_call(['samtools', 'view', '-b', '-F', '2048', '-F', '256', '-f', '2', '--threads', str(threads - 1), '-o', ANY, bam], check=True)
    subprocess.run.assert_any_call(['samtools', 'sort', '--threads', str(threads - 1), '-o', output, ANY], check=True)
    assert subprocess.run.call_args_list[0].args[0][12] == subprocess.run.call_args_list[1].args[0][6]


def test_filter_mapped_paired_qualitythreads(testdir, mock_testclass):
    bam = 'POLR2A.bam'
    output = 'POLR2A-out.bam'
    quality = 20
    threads = 3
    subprocess.run = MagicMock(side_effect=create_file)
    fb.filter_mapped(bam, output, True, quality=quality, threads=threads)
    subprocess.run.assert_any_call(['samtools', 'view', '-b', '-F', '2048', '-F', '256', '-f', '2', '-q', str(quality), '--threads', str(threads - 1), '-o', ANY, bam], check=True)
    subprocess.run.assert_any_call(['samtools', 'sort', '--threads', str(threads - 1), '-o', output, ANY], check=True)
    assert subprocess.run.call_args_list[0].args[0][14] == subprocess.run.call_args_list[1].args[0][6]


def test_filter_mapped_paired_singlethread(testdir, mock_testclass):
    bam = 'POLR2A.bam'
    output = 'POLR2A-out.bam'
    threads = 1
    subprocess.run = MagicMock(side_effect=create_file)
    fb.filter_mapped(bam, output, True, threads=threads)
    subprocess.run.assert_any_call(['samtools', 'view', '-b', '-F', '2048', '-F', '256', '-f', '2', '-o', ANY, bam], check=True)
    subprocess.run.assert_any_call(['samtools', 'sort', '-o', output, ANY], check=True)
    assert subprocess.run.call_args_list[0].args[0][10] == subprocess.run.call_args_list[1].args[0][4]


def test_remove_duplicates(testdir, mock_testclass):
    bam = 'POLR2A.bam'
    output = 'POLR2A-out.bam'
    subprocess.run = MagicMock(side_effect=[create_file, create_file_fixmate, create_file, create_file_markdup, create_file])
    fb.remove_duplicates(bam, output)
    subprocess.run.assert_any_call(['samtools', 'sort', '-n', '-o', ANY, bam], check=True)
    subprocess.run.assert_any_call(['samtools', 'fixmate', '-m', ANY, ANY], check=True)
    subprocess.run.assert_any_call(['samtools', 'sort', '-o', ANY, ANY], check=True)
    subprocess.run.assert_any_call(['samtools', 'markdup', '-r', ANY, ANY], check=True)
    subprocess.run.assert_any_call(['samtools', 'sort', '-o', output, ANY], check=True)
    assert subprocess.run.call_args_list[0].args[0][4] == subprocess.run.call_args_list[1].args[0][3]
    assert subprocess.run.call_args_list[1].args[0][4] == subprocess.run.call_args_list[2].args[0][4]
    assert subprocess.run.call_args_list[2].args[0][3] == subprocess.run.call_args_list[3].args[0][3]
    assert subprocess.run.call_args_list[3].args[0][4] == subprocess.run.call_args_list[3].args[0][4]


def test_remove_duplicates_threads(testdir, mock_testclass):
    bam = 'POLR2A.bam'
    output = 'POLR2A-out.bam'
    threads = 3
    subprocess.run = MagicMock(side_effect=[create_file, create_file_fixmate, create_file, create_file_markdup, create_file])
    fb.remove_duplicates(bam, output, threads)
    subprocess.run.assert_any_call(['samtools', 'sort', '-n', '--threads', str(threads - 1), '-o', ANY, bam], check=True)
    subprocess.run.assert_any_call(['samtools', 'fixmate', '-m', '--threads', str(threads - 1), ANY, ANY], check=True)
    subprocess.run.assert_any_call(['samtools', 'sort', '--threads', str(threads - 1), '-o', ANY, ANY], check=True)
    subprocess.run.assert_any_call(['samtools', 'markdup', '-r', '--threads', str(threads - 1), ANY, ANY], check=True)
    subprocess.run.assert_any_call(['samtools', 'sort', '--threads', str(threads - 1), '-o', output, ANY], check=True)
    assert subprocess.run.call_args_list[0].args[0][6] == subprocess.run.call_args_list[1].args[0][5]
    assert subprocess.run.call_args_list[1].args[0][6] == subprocess.run.call_args_list[2].args[0][6]
    assert subprocess.run.call_args_list[2].args[0][5] == subprocess.run.call_args_list[3].args[0][5]
    assert subprocess.run.call_args_list[3].args[0][6] == subprocess.run.call_args_list[3].args[0][6]


def test_remove_duplicates_singlethread(testdir, mock_testclass):
    bam = 'POLR2A.bam'
    output = 'POLR2A-out.bam'
    threads = 1
    subprocess.run = MagicMock(side_effect=[create_file, create_file_fixmate, create_file, create_file_markdup, create_file])
    fb.remove_duplicates(bam, output, threads)
    subprocess.run.assert_any_call(['samtools', 'sort', '-n', '-o', ANY, bam], check=True)
    subprocess.run.assert_any_call(['samtools', 'fixmate', '-m', ANY, ANY], check=True)
    subprocess.run.assert_any_call(['samtools', 'sort', '-o', ANY, ANY], check=True)
    subprocess.run.assert_any_call(['samtools', 'markdup', '-r', ANY, ANY], check=True)
    subprocess.run.assert_any_call(['samtools', 'sort', '-o', output, ANY], check=True)
    assert subprocess.run.call_args_list[0].args[0][4] == subprocess.run.call_args_list[1].args[0][3]
    assert subprocess.run.call_args_list[1].args[0][4] == subprocess.run.call_args_list[2].args[0][4]
    assert subprocess.run.call_args_list[2].args[0][3] == subprocess.run.call_args_list[3].args[0][3]
    assert subprocess.run.call_args_list[3].args[0][4] == subprocess.run.call_args_list[3].args[0][4]


def test_sort(testdir, mock_testclass):
    bam = 'POLR2A.bam'
    output = 'POLR2A-out.bam'
    subprocess.run = MagicMock()
    fb.sort(bam, output)
    subprocess.run.assert_any_call(['samtools', 'sort', '-o', output, bam], check=True)


def test_sort_threads(testdir, mock_testclass):
    bam = 'POLR2A.bam'
    output = 'POLR2A-out.bam'
    threads = 3
    subprocess.run = MagicMock()
    fb.sort(bam, output, threads)
    subprocess.run.assert_any_call(['samtools', 'sort', '--threads', str(threads - 1), '-o', output, bam], check=True)


def test_sort_singlethread(testdir, mock_testclass):
    bam = 'POLR2A.bam'
    output = 'POLR2A-out.bam'
    threads = 1
    subprocess.run = MagicMock()
    fb.sort(bam, output, threads)
    subprocess.run.assert_any_call(['samtools', 'sort', '-o', output, bam], check=True)
