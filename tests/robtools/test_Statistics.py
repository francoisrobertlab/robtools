import logging
from pathlib import Path
import subprocess
from unittest.mock import MagicMock, ANY

import click
from click.testing import CliRunner
import pytest

from robtools import Split
from robtools import Statistics as s
from robtools.bed import Bed


@pytest.fixture
def mock_testclass():
    statistics_samples = s.statistics_samples
    compute_statistics = s.compute_statistics
    headers = s.headers
    sample_statistics = s.sample_statistics
    flagstat_total = s.flagstat_total
    splits = Split.splits
    count_bed = Bed.count_bed
    run = subprocess.run
    yield
    s.statistics_samples = statistics_samples
    s.compute_statistics = compute_statistics
    s.headers = headers
    s.sample_statistics = sample_statistics
    s.flagstat_total = flagstat_total
    Split.splits = splits
    Bed.count_bed = count_bed
    subprocess.run = run


def splits(*args, **kwargs):
    sample = args[0]
    logging.warning('args: {}'.format(args))
    return [sample + '-100-110', sample + '-110-120', sample + '-120-140']
       

def test_statistics(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    s.statistics_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(s.statistics, ['-s', samples])
    assert result.exit_code == 0
    s.statistics_samples.assert_called_once_with(samples, 'dataset.txt', 'statistics.txt')


def test_statistics_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    datasets = Path(__file__).parent.joinpath('dataset.txt')
    output = 'out.txt'
    s.statistics_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(s.statistics, ['-s', samples, '-d', datasets, '-o', output])
    assert result.exit_code == 0
    s.statistics_samples.assert_called_once_with(samples, datasets, output)


def test_statistics_samplesnotexists(testdir, mock_testclass):
    samples = 'samples.txt'
    s.statistics_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(s.statistics, ['-s', samples])
    assert result.exit_code != 0
    s.statistics_samples.assert_not_called()


def test_statistics_datasetsnotexists(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    datasets = 'dataset.txt'
    s.statistics_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(s.statistics, ['-s', samples, '-d', datasets])
    assert result.exit_code == 0
    s.statistics_samples.assert_called_once_with(samples, datasets, 'statistics.txt')


def test_statistics_samples(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    datasets = Path(__file__).parent.joinpath('dataset.txt')
    s.compute_statistics = MagicMock()
    s.statistics_samples(samples, datasets)
    s.compute_statistics.assert_called_once_with(['POLR2A', 'ASDURF', 'POLR1C'], ['POLR2A', 'ASDURF', 'POLR1C'], 'statistics.txt')


def test_statistics_samples_datasetsnotexists(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    datasets = 'dataset.txt'
    s.compute_statistics = MagicMock()
    s.statistics_samples(samples, datasets)
    s.compute_statistics.assert_called_once_with(['POLR2A', 'ASDURF', 'POLR1C'], [], 'statistics.txt')


def test_statistics_samples_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    sample_pandas = ['samples-pandas']
    datasets = Path(__file__).parent.joinpath('dataset.txt')
    datasets_pandas = ['datasets-pandas']
    output = 'out.txt'
    s.compute_statistics = MagicMock()
    s.statistics_samples(samples, datasets, output)
    s.compute_statistics.assert_called_once_with(['POLR2A', 'ASDURF', 'POLR1C'], ['POLR2A', 'ASDURF', 'POLR1C'], output)


def test_compute_statistics(testdir, mock_testclass):
    samples = ['POLR2A', 'ASDURF']
    datasets = ['POLR1C']
    output = 'out.txt'
    splits = ['100-110', '120-130']
    s.headers = MagicMock(return_value=(['Sample', 'Total reads', 'Mapped reads', 'Deduplicated reads', '100-110', '120-130'], splits))
    s.sample_statistics = MagicMock(side_effect=[['POLR2A', 500, 400, 300, 60, 40], ['ASDURF', 550, 450, 350, 70, 50], ['POLR1C', '', '', 250, 50, 30]])
    s.compute_statistics(samples, datasets, output)
    s.headers.assert_called_once_with(samples, datasets)
    s.sample_statistics.assert_any_call(samples[0], splits)
    s.sample_statistics.assert_any_call(samples[1], splits)
    s.sample_statistics.assert_any_call(datasets[0], splits)
    with open(output, 'r') as infile:
        assert infile.readline() == 'Sample\tTotal reads\tMapped reads\tDeduplicated reads\t100-110\t120-130\n'
        assert infile.readline() == 'POLR2A\t500\t400\t300\t60\t40\n'
        assert infile.readline() == 'ASDURF\t550\t450\t350\t70\t50\n'
        assert infile.readline() == 'POLR1C\t\t\t250\t50\t30\n'
        assert infile.readline() == ''


def test_headers(testdir, mock_testclass):
    samples = ['POLR2A', 'ASDURF']
    datasets = ['POLR1C']
    Split.splits = MagicMock(side_effect=splits)
    headers, splits_headers = s.headers(samples, datasets)
    assert headers[0] == 'Sample'
    assert headers[1] == 'Total reads'
    assert headers[2] == 'Mapped reads'
    assert headers[3] == 'Deduplicated reads'
    assert headers[4] == '100-110'
    assert headers[5] == '110-120'
    assert headers[6] == '120-140'
    assert len(headers) == 7
    assert splits_headers[0] == '100-110'
    assert splits_headers[1] == '110-120'
    assert splits_headers[2] == '120-140'
    assert len(splits_headers) == 3

    
def test_headers_missmatch(testdir, mock_testclass):
    samples = ['POLR2A', 'ASDURF']
    datasets = ['POLR1C']
    sample1_headers = [samples[0] + '-100-110', samples[0] + '-110-120', samples[0] + '-130-140']
    sample2_headers = [samples[1] + '-100-110', samples[1] + '-110-120', samples[1] + '-130-140']
    dataset1_headers = [datasets[0] + '-100-110', datasets[0] + '-120-130', datasets[0] + '-140-150']
    Split.splits = MagicMock(side_effect=[sample1_headers, sample2_headers, dataset1_headers])
    headers, splits_headers = s.headers(samples, datasets)
    assert headers[0] == 'Sample'
    assert headers[1] == 'Total reads'
    assert headers[2] == 'Mapped reads'
    assert headers[3] == 'Deduplicated reads'
    assert headers[4] == '100-110'
    assert headers[5] == '110-120'
    assert headers[6] == '120-130'
    assert headers[7] == '130-140'
    assert headers[8] == '140-150'
    assert len(headers) == 9
    assert splits_headers[0] == '100-110'
    assert splits_headers[1] == '110-120'
    assert splits_headers[2] == '120-130'
    assert splits_headers[3] == '130-140'
    assert splits_headers[4] == '140-150'
    assert len(splits_headers) == 5


def test_sample_statistics(testdir, mock_testclass):
    sample = 'POLR2A'
    Path(sample + '.bam').touch()
    Path(sample + '-filtered.bam').touch()
    Path(sample + '.bed').touch()
    splits = ['100-110', '120-130']
    for split in splits:
        Path(sample + '-' + split + '.bed').touch()
    s.flagstat_total = MagicMock(side_effect=[300, 200])
    Bed.count_bed = MagicMock(side_effect=[150, 50, 40])
    stats = s.sample_statistics(sample, splits)
    assert stats[0] == sample
    assert stats[1] == 300
    assert stats[2] == 200
    assert stats[3] == 150 * 2
    assert stats[4] == 50
    assert stats[5] == 40
    assert len(stats) == 6
    s.flagstat_total.assert_any_call(sample + '.bam')
    s.flagstat_total.assert_any_call(sample + '-filtered.bam')
    Bed.count_bed.assert_any_call(sample + '.bed')
    Bed.count_bed.assert_any_call(sample + '-100-110.bed')
    Bed.count_bed.assert_any_call(sample + '-120-130.bed')


def test_sample_statistics_notexists(testdir, mock_testclass):
    sample = 'POLR2A'
    splits = ['100-110', '120-130']
    s.flagstat_total = MagicMock(side_effect=[300, 200])
    Bed.count_bed = MagicMock(side_effect=[150, 50, 40])
    stats = s.sample_statistics(sample, splits)
    assert stats[0] == sample
    assert stats[1] == ''
    assert stats[2] == ''
    assert stats[3] == ''
    assert stats[4] == ''
    assert stats[5] == ''
    assert len(stats) == 6
    s.flagstat_total.assert_not_called()
    Bed.count_bed.assert_not_called()


def test_flagstat_total(testdir, mock_testclass):
    bam = 'POLR2A.bam'
    output = MagicMock()
    output.stdout = MagicMock()
    output.stdout.decode = MagicMock(return_value='5400')
    subprocess.run = MagicMock(return_value=output)
    total = s.flagstat_total(bam)
    subprocess.run.assert_any_call(['samtools', 'flagstat', bam], capture_output=True, check=True)
    assert total == '5400'


def test_flagstat_total_2(testdir, mock_testclass):
    bam = 'POLR2A.bam'
    output = MagicMock()
    output.stdout = MagicMock()
    output.stdout.decode = MagicMock(return_value='200')
    subprocess.run = MagicMock(return_value=output)
    total = s.flagstat_total(bam)
    subprocess.run.assert_any_call(['samtools', 'flagstat', bam], capture_output=True, check=True)
    assert total == '200'
