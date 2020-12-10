import logging
import os
from pathlib import Path
import pytest
from shutil import copyfile
import subprocess
from unittest.mock import MagicMock, ANY

import click
from click.testing import CliRunner
from more_itertools.more import side_effect

from robtools import GenomeCoverage as gc
from robtools import Split as sb
from robtools.bed import Bed

BASE_SCALE = 1000000


@pytest.fixture
def mock_testclass():
    genome_coverage_samples = gc.genome_coverage_samples
    sample_splits_genome_coverage = gc.sample_splits_genome_coverage
    genome_coverage = gc.genome_coverage
    coverage = gc.coverage
    splits = sb.splits
    sort = Bed.sort
    count_bed = Bed.count_bed
    bedgraph_to_bigwig = Bed.bedgraph_to_bigwig
    run = subprocess.run
    yield
    gc.genome_coverage_samples = genome_coverage_samples
    gc.sample_splits_genome_coverage = sample_splits_genome_coverage
    gc.genome_coverage = genome_coverage
    gc.coverage = coverage
    sb.splits = splits
    Bed.sort = sort
    Bed.count_bed = count_bed
    Bed.bedgraph_to_bigwig = bedgraph_to_bigwig
    subprocess.run = run
    
    
def create_file(*args, **kwargs):
    if 'stdout' in kwargs:
        outfile = kwargs['stdout']
        outfile.write('test')
    elif '-o' in args[0]:
        output = args[0][args[0].index('-o') + 1]
        with open(output, 'w') as outfile:
            outfile.write('test')


def create_file_sort(*args, **kwargs):
    output = args[1]
    with open(output, 'w') as outfile:
        outfile.write('test')


def test_genomecov(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = 'sacCer3.chrom.sizes'
    copyfile(Path(__file__).parent.joinpath('sizes.txt'), genome)
    gc.genome_coverage_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(gc.genomecov, ['-s', samples])
    assert result.exit_code == 0
    gc.genome_coverage_samples.assert_called_once_with(samples, genome, None, None, '', '-cov', None, None, None, ())


def test_genomecov_five(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = 'sacCer3.chrom.sizes'
    copyfile(Path(__file__).parent.joinpath('sizes.txt'), genome)
    gc.genome_coverage_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(gc.genomecov, ['-s', samples, '-5'])
    assert result.exit_code == 0
    gc.genome_coverage_samples.assert_called_once_with(samples, genome, None, None, '', '-cov', None, None, None, ('-5',))


def test_genomecov_three(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = 'sacCer3.chrom.sizes'
    copyfile(Path(__file__).parent.joinpath('sizes.txt'), genome)
    gc.genome_coverage_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(gc.genomecov, ['-s', samples, '-3'])
    assert result.exit_code == 0
    gc.genome_coverage_samples.assert_called_once_with(samples, genome, None, None, '', '-cov', None, None, None, ('-3',))


def test_genomecov_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = Path(__file__).parent.joinpath('sizes.txt')
    scale = 1.5
    strand = '+'
    input_suffix = '-forcov'
    output_suffix = '-outcov'
    index = 1
    gc.genome_coverage_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(gc.genomecov, ['-s', samples, '-g', genome, '-scale', scale, '-strand', strand, '--input-suffix', input_suffix, '--output-suffix', output_suffix, '--index', index])
    assert result.exit_code == 0
    gc.genome_coverage_samples.assert_called_once_with(samples, genome, scale, strand, input_suffix, output_suffix, None, None, index, ())


def test_genomecov_parameters_scalesuffixes(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = Path(__file__).parent.joinpath('sizes.txt')
    strand = '+'
    input_suffix = '-forcov'
    output_suffix = '-outcov'
    spike_suffix = '-pombe'
    control_suffix = '-input'
    index = 1
    gc.genome_coverage_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(gc.genomecov, ['-s', samples, '-g', genome, '-strand', strand, '--input-suffix', input_suffix, '--output-suffix', output_suffix, '--spike-suffix', spike_suffix, '--control-suffix', control_suffix, '--index', index])
    assert result.exit_code == 0
    gc.genome_coverage_samples.assert_called_once_with(samples, genome, None, strand, input_suffix, output_suffix, spike_suffix, control_suffix, index, ())


def test_genomecov_scale_and_spikesuffix(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = Path(__file__).parent.joinpath('sizes.txt')
    scale = 1.5
    spike_suffix = '-pombe'
    gc.genome_coverage_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(gc.genomecov, ['-s', samples, '-g', genome, '-scale', scale, '--spike-suffix', spike_suffix])
    assert result.exit_code > 0
    gc.genome_coverage_samples.assert_not_called()


def test_genomecov_scale_and_controlsuffix(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = Path(__file__).parent.joinpath('sizes.txt')
    scale = 1.5
    control_suffix = '-input'
    gc.genome_coverage_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(gc.genomecov, ['-s', samples, '-g', genome, '-scale', scale, '--control-suffix', control_suffix])
    assert result.exit_code > 0
    gc.genome_coverage_samples.assert_not_called()


def test_genomecov_sameinoutsuffix(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = Path(__file__).parent.joinpath('sizes.txt')
    input_suffix = '-forcov'
    gc.genome_coverage_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(gc.genomecov, ['-s', samples, '-g', genome, '--input-suffix', input_suffix, '--output-suffix', input_suffix])
    assert result.exit_code > 0
    gc.genome_coverage_samples.assert_not_called()


def test_genomecov_onlyoutputsuffix(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = Path(__file__).parent.joinpath('sizes.txt')
    output_suffix = '-outcov'
    gc.genome_coverage_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(gc.genomecov, ['-s', samples, '-g', genome, '--output-suffix', output_suffix])
    assert result.exit_code == 0
    gc.genome_coverage_samples.assert_called_once_with(samples, genome, None, None, '', output_suffix, None, None, None, ())


def test_genomecov_samplesnotexists(testdir, mock_testclass):
    samples = 'samples.txt'
    genome = 'sacCer3.chrom.sizes'
    copyfile(Path(__file__).parent.joinpath('sizes.txt'), genome)
    gc.genome_coverage_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(gc.genomecov, ['-s', samples])
    assert result.exit_code > 0
    gc.genome_coverage_samples.assert_not_called()


def test_genomecov_genomenotexists(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = 'sacCer3.chrom.sizes'
    gc.genome_coverage_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(gc.genomecov, ['-s', samples, '-g', genome])
    assert result.exit_code > 0
    gc.genome_coverage_samples.assert_not_called()


def test_genome_coverage_samples(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = 'sacCer3.chrom.sizes'
    copyfile(Path(__file__).parent.joinpath('sizes.txt'), genome)
    gc.sample_splits_genome_coverage = MagicMock()
    gc.genome_coverage_samples(samples)
    gc.sample_splits_genome_coverage.assert_any_call('POLR2A', genome, None, None, '', '-cov', None, None, ())
    gc.sample_splits_genome_coverage.assert_any_call('ASDURF', genome, None, None, '', '-cov', None, None, ())
    gc.sample_splits_genome_coverage.assert_any_call('POLR1C', genome, None, None, '', '-cov', None, None, ())


def test_genome_coverage_samples_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = 'sacCer3.chrom.sizes'
    copyfile(Path(__file__).parent.joinpath('sizes.txt'), genome)
    scale = 1.5
    strand = '+'
    input_suffix = '-forcov'
    output_suffix = '-outcov'
    spike_suffix = '-pombe'
    control_suffix = '-input'
    gc.sample_splits_genome_coverage = MagicMock()
    gc.genome_coverage_samples(samples, genome, scale, strand, input_suffix, output_suffix, spike_suffix, control_suffix, genomecov_args=('-5',))
    gc.sample_splits_genome_coverage.assert_any_call('POLR2A', genome, scale, strand, input_suffix, output_suffix, spike_suffix, control_suffix, ('-5',))
    gc.sample_splits_genome_coverage.assert_any_call('ASDURF', genome, scale, strand, input_suffix, output_suffix, spike_suffix, control_suffix, ('-5',))
    gc.sample_splits_genome_coverage.assert_any_call('POLR1C', genome, scale, strand, input_suffix, output_suffix, spike_suffix, control_suffix, ('-5',))


def test_genome_coverage_samples_all_five(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = Path(__file__).parent.joinpath('sizes.txt')
    gc.sample_splits_genome_coverage = MagicMock()
    gc.genome_coverage_samples(samples, genome, genomecov_args=('-5',))
    gc.sample_splits_genome_coverage.assert_any_call('POLR2A', genome, None, None, '', '-cov', None, None, ('-5',))
    gc.sample_splits_genome_coverage.assert_any_call('ASDURF', genome, None, None, '', '-cov', None, None, ('-5',))
    gc.sample_splits_genome_coverage.assert_any_call('POLR1C', genome, None, None, '', '-cov', None, None, ('-5',))


def test_genome_coverage_samples_second_five(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = Path(__file__).parent.joinpath('sizes.txt')
    gc.sample_splits_genome_coverage = MagicMock()
    gc.genome_coverage_samples(samples, genome, index=1, genomecov_args=('-5',))
    gc.sample_splits_genome_coverage.assert_called_once_with('ASDURF', genome, None, None, '', '-cov', None, None, ('-5',))


def test_genome_coverage_samples_all_three(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = Path(__file__).parent.joinpath('sizes.txt')
    gc.sample_splits_genome_coverage = MagicMock()
    gc.genome_coverage_samples(samples, genome, genomecov_args=('-3',))
    gc.sample_splits_genome_coverage.assert_any_call('POLR2A', genome, None, None, '', '-cov', None, None, ('-3',))
    gc.sample_splits_genome_coverage.assert_any_call('ASDURF', genome, None, None, '', '-cov', None, None, ('-3',))
    gc.sample_splits_genome_coverage.assert_any_call('POLR1C', genome, None, None, '', '-cov', None, None, ('-3',))


def test_genome_coverage_samples_second_three(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = Path(__file__).parent.joinpath('sizes.txt')
    gc.sample_splits_genome_coverage = MagicMock()
    gc.genome_coverage_samples(samples, genome, genomecov_args=('-3',), index=1)
    gc.sample_splits_genome_coverage.assert_called_once_with('ASDURF', genome, None, None, '', '-cov', None, None, ('-3',))


def test_genome_coverage_samples_all_scale(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = Path(__file__).parent.joinpath('sizes.txt')
    scale = 1.5
    gc.sample_splits_genome_coverage = MagicMock()
    gc.genome_coverage_samples(samples, genome, scale=scale)
    gc.sample_splits_genome_coverage.assert_any_call('POLR2A', genome, scale, None, '', '-cov', None, None, ())
    gc.sample_splits_genome_coverage.assert_any_call('ASDURF', genome, scale, None, '', '-cov', None, None, ())
    gc.sample_splits_genome_coverage.assert_any_call('POLR1C', genome, scale, None, '', '-cov', None, None, ())


def test_genome_coverage_samples_second_scale(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = Path(__file__).parent.joinpath('sizes.txt')
    scale = 1.5
    gc.sample_splits_genome_coverage = MagicMock()
    gc.genome_coverage_samples(samples, genome, scale=scale, index=1)
    gc.sample_splits_genome_coverage.assert_called_once_with('ASDURF', genome, scale, None, '', '-cov', None, None, ())


def test_genome_coverage_samples_all_scale_negativestrand(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = Path(__file__).parent.joinpath('sizes.txt')
    scale = 1.5
    strand = '-'
    gc.sample_splits_genome_coverage = MagicMock()
    gc.genome_coverage_samples(samples, genome, scale=scale, strand=strand)
    gc.sample_splits_genome_coverage.assert_any_call('POLR2A', genome, scale, strand, '', '-cov', None, None, ())
    gc.sample_splits_genome_coverage.assert_any_call('ASDURF', genome, scale, strand, '', '-cov', None, None, ())
    gc.sample_splits_genome_coverage.assert_any_call('POLR1C', genome, scale, strand, '', '-cov', None, None, ())


def test_genome_coverage_samples_second_scale_negativestrand(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = Path(__file__).parent.joinpath('sizes.txt')
    scale = 1.5
    strand = '-'
    gc.sample_splits_genome_coverage = MagicMock()
    gc.genome_coverage_samples(samples, genome, scale=scale, strand=strand, index=1)
    gc.sample_splits_genome_coverage.assert_called_once_with('ASDURF', genome, scale, strand, '', '-cov', None, None, ())


def test_genome_coverage_samples_all_scale_positivestrand(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = Path(__file__).parent.joinpath('sizes.txt')
    scale = 1.5
    strand = '+'
    gc.sample_splits_genome_coverage = MagicMock()
    gc.genome_coverage_samples(samples, genome, scale=scale, strand=strand)
    gc.sample_splits_genome_coverage.assert_any_call('POLR2A', genome, scale, strand, '', '-cov', None, None, ())
    gc.sample_splits_genome_coverage.assert_any_call('ASDURF', genome, scale, strand, '', '-cov', None, None, ())
    gc.sample_splits_genome_coverage.assert_any_call('POLR1C', genome, scale, strand, '', '-cov', None, None, ())


def test_genome_coverage_samples_second_scale_positivestrand(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    genome = Path(__file__).parent.joinpath('sizes.txt')
    scale = 1.5
    strand = '+'
    gc.sample_splits_genome_coverage = MagicMock()
    gc.genome_coverage_samples(samples, genome, scale=scale, strand=strand, index=1)
    gc.sample_splits_genome_coverage.assert_called_once_with('ASDURF', genome, scale, strand, '', '-cov', None, None, ())

    
def test_sample_splits_genome_coverage(testdir, mock_testclass):
    sample = 'POLR2A'
    genome = 'human.sizes'
    split1 = sample + '-100-110'
    split2 = sample + '-110-120'
    sb.splits = MagicMock(return_value=[split1, split2])
    gc.genome_coverage = MagicMock()
    gc.sample_splits_genome_coverage(sample, genome)
    sb.splits.assert_called_once_with(sample)
    gc.genome_coverage.assert_any_call(sample, genome, None, None, '', '-cov', None, None, ())
    gc.genome_coverage.assert_any_call(split1, genome, None, None, '', '-cov', None, None, ())
    gc.genome_coverage.assert_any_call(split2, genome, None, None, '', '-cov', None, None, ())


def test_sample_splits_genome_coverage_parameters(testdir, mock_testclass):
    sample = 'POLR2A'
    genome = 'human.sizes'
    split1 = sample + '-100-110'
    split2 = sample + '-110-120'
    scale = 1.5
    strand = '+'
    input_suffix = '-forcov'
    output_suffix = '-outcov'
    spike_suffix = '-pombe'
    control_suffix = '-input'
    sb.splits = MagicMock(return_value=[split1, split2])
    gc.genome_coverage = MagicMock()
    gc.sample_splits_genome_coverage(sample, genome, scale, strand, input_suffix, output_suffix, spike_suffix, control_suffix, ('-5',))
    sb.splits.assert_called_once_with(sample)
    gc.genome_coverage.assert_any_call(sample, genome, scale, strand, input_suffix, output_suffix, spike_suffix, control_suffix, ('-5',))
    gc.genome_coverage.assert_any_call(split1, genome, scale, strand, input_suffix, output_suffix, spike_suffix, control_suffix, ('-5',))
    gc.genome_coverage.assert_any_call(split2, genome, scale, strand, input_suffix, output_suffix, spike_suffix, control_suffix, ('-5',))


def test_sample_splits_genome_coverage_five(testdir, mock_testclass):
    sample = 'POLR2A'
    genome = 'human.sizes'
    split1 = sample + '-100-110'
    split2 = sample + '-110-120'
    sb.splits = MagicMock(return_value=[split1, split2])
    gc.genome_coverage = MagicMock()
    gc.sample_splits_genome_coverage(sample, genome, genomecov_args=('-5'))
    sb.splits.assert_called_once_with(sample)
    gc.genome_coverage.assert_any_call(sample, genome, None, None, '', '-cov', None, None, ('-5'))
    gc.genome_coverage.assert_any_call(split1, genome, None, None, '', '-cov', None, None, ('-5'))
    gc.genome_coverage.assert_any_call(split2, genome, None, None, '', '-cov', None, None, ('-5'))


def test_sample_splits_genome_coverage_three(testdir, mock_testclass):
    sample = 'POLR2A'
    genome = 'human.sizes'
    split1 = sample + '-100-110'
    split2 = sample + '-110-120'
    sb.splits = MagicMock(return_value=[split1, split2])
    gc.genome_coverage = MagicMock()
    gc.sample_splits_genome_coverage(sample, genome, genomecov_args=('-3'))
    sb.splits.assert_called_once_with(sample)
    gc.genome_coverage.assert_any_call(sample, genome, None, None, '', '-cov', None, None, ('-3'))
    gc.genome_coverage.assert_any_call(split1, genome, None, None, '', '-cov', None, None, ('-3'))
    gc.genome_coverage.assert_any_call(split2, genome, None, None, '', '-cov', None, None, ('-3'))


def test_sample_splits_genome_coverage_scale(testdir, mock_testclass):
    sample = 'POLR2A'
    genome = 'human.sizes'
    split1 = sample + '-100-110'
    split2 = sample + '-110-120'
    scale = 1.5
    sb.splits = MagicMock(return_value=[split1, split2])
    gc.genome_coverage = MagicMock()
    gc.sample_splits_genome_coverage(sample, genome, scale)
    sb.splits.assert_called_once_with(sample)
    gc.genome_coverage.assert_any_call(sample, genome, scale, None, '', '-cov', None, None, ())
    gc.genome_coverage.assert_any_call(split1, genome, scale, None, '', '-cov', None, None, ())
    gc.genome_coverage.assert_any_call(split2, genome, scale, None, '', '-cov', None, None, ())


def test_sample_splits_genome_coverage_negativestrand(testdir, mock_testclass):
    sample = 'POLR2A'
    genome = 'human.sizes'
    split1 = sample + '-100-110'
    split2 = sample + '-110-120'
    strand = '-'
    sb.splits = MagicMock(return_value=[split1, split2])
    gc.genome_coverage = MagicMock()
    gc.sample_splits_genome_coverage(sample, genome, strand=strand)
    sb.splits.assert_called_once_with(sample)
    gc.genome_coverage.assert_any_call(sample, genome, None, strand, '', '-cov', None, None, ())
    gc.genome_coverage.assert_any_call(split1, genome, None, strand, '', '-cov', None, None, ())
    gc.genome_coverage.assert_any_call(split2, genome, None, strand, '', '-cov', None, None, ())


def test_sample_splits_genome_coverage_scale_negativestrand(testdir, mock_testclass):
    sample = 'POLR2A'
    genome = 'human.sizes'
    split1 = sample + '-100-110'
    split2 = sample + '-110-120'
    scale = 1.5
    strand = '-'
    sb.splits = MagicMock(return_value=[split1, split2])
    gc.genome_coverage = MagicMock()
    gc.sample_splits_genome_coverage(sample, genome, scale=scale, strand=strand)
    sb.splits.assert_called_once_with(sample)
    gc.genome_coverage.assert_any_call(sample, genome, scale, strand, '', '-cov', None, None, ())
    gc.genome_coverage.assert_any_call(split1, genome, scale, strand, '', '-cov', None, None, ())
    gc.genome_coverage.assert_any_call(split2, genome, scale, strand, '', '-cov', None, None, ())


def test_sample_splits_genome_coverage_positivestrand(testdir, mock_testclass):
    sample = 'POLR2A'
    genome = 'human.sizes'
    split1 = sample + '-100-110'
    split2 = sample + '-110-120'
    strand = '+'
    sb.splits = MagicMock(return_value=[split1, split2])
    gc.genome_coverage = MagicMock()
    gc.sample_splits_genome_coverage(sample, genome, strand=strand)
    sb.splits.assert_called_once_with(sample)
    gc.genome_coverage.assert_any_call(sample, genome, None, strand, '', '-cov', None, None, ())
    gc.genome_coverage.assert_any_call(split1, genome, None, strand, '', '-cov', None, None, ())
    gc.genome_coverage.assert_any_call(split2, genome, None, strand, '', '-cov', None, None, ())


def test_sample_splits_genome_coverage_scale_positivestrand(testdir, mock_testclass):
    sample = 'POLR2A'
    genome = 'human.sizes'
    split1 = sample + '-100-110'
    split2 = sample + '-110-120'
    scale = 1.5
    strand = '+'
    sb.splits = MagicMock(return_value=[split1, split2])
    gc.genome_coverage = MagicMock()
    gc.sample_splits_genome_coverage(sample, genome, scale=scale, strand=strand)
    sb.splits.assert_called_once_with(sample)
    gc.genome_coverage.assert_any_call(sample, genome, scale, strand, '', '-cov', None, None, ())
    gc.genome_coverage.assert_any_call(split1, genome, scale, strand, '', '-cov', None, None, ())
    gc.genome_coverage.assert_any_call(split2, genome, scale, strand, '', '-cov', None, None, ())


def test_genome_coverage(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    cov = sample + '-cov.bed'
    bw = sample + '-cov.bw'
    genome = 'human.sizes'
    count = 2000000
    Bed.count_bed = MagicMock(return_value=count)
    gc.coverage = MagicMock()
    Bed.bedgraph_to_bigwig = MagicMock()
    gc.genome_coverage(sample, genome)
    Bed.count_bed.assert_called_once_with(bed)
    gc.coverage.assert_called_once_with(bed, cov, genome, sample, BASE_SCALE / count, None, ())
    Bed.bedgraph_to_bigwig.assert_called_once_with(cov, bw, genome)


def test_genome_coverage_suffix(testdir, mock_testclass):
    sample = 'POLR2A'
    input_suffix = '-forcov'
    output_suffix = '-outcov'
    bed = sample + input_suffix + '.bed'
    cov = sample + output_suffix + '.bed'
    bw = sample + output_suffix + '.bw'
    genome = 'human.sizes'
    count = 2000000
    Bed.count_bed = MagicMock(return_value=count)
    gc.coverage = MagicMock()
    Bed.bedgraph_to_bigwig = MagicMock()
    gc.genome_coverage(sample, genome, input_suffix=input_suffix, output_suffix=output_suffix)
    Bed.count_bed.assert_called_once_with(bed)
    gc.coverage.assert_called_once_with(bed, cov, genome, sample, BASE_SCALE / count, None, ())
    Bed.bedgraph_to_bigwig.assert_called_once_with(cov, bw, genome)


def test_genome_coverage_five(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    cov = sample + '-cov.bed'
    bw = sample + '-cov.bw'
    genome = 'human.sizes'
    count = 2000000
    Bed.count_bed = MagicMock(return_value=count)
    gc.coverage = MagicMock()
    Bed.bedgraph_to_bigwig = MagicMock()
    gc.genome_coverage(sample, genome, genomecov_args=('-5'))
    Bed.count_bed.assert_called_once_with(bed)
    gc.coverage.assert_called_once_with(bed, cov, genome, sample, BASE_SCALE / count, None, ('-5'))
    Bed.bedgraph_to_bigwig.assert_called_once_with(cov, bw, genome)


def test_genome_coverage_three(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    cov = sample + '-cov.bed'
    bw = sample + '-cov.bw'
    genome = 'human.sizes'
    count = 2000000
    Bed.count_bed = MagicMock(return_value=count)
    gc.coverage = MagicMock()
    Bed.bedgraph_to_bigwig = MagicMock()
    gc.genome_coverage(sample, genome, genomecov_args=('-3'))
    Bed.count_bed.assert_called_once_with(bed)
    gc.coverage.assert_called_once_with(bed, cov, genome, sample, BASE_SCALE / count, None, ('-3'))
    Bed.bedgraph_to_bigwig.assert_called_once_with(cov, bw, genome)


def test_genome_coverage_scale(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    cov = sample + '-cov.bed'
    bw = sample + '-cov.bw'
    genome = 'human.sizes'
    scale = 1.5
    Bed.count_bed = MagicMock()
    gc.coverage = MagicMock()
    Bed.bedgraph_to_bigwig = MagicMock()
    gc.genome_coverage(sample, genome, scale=scale)
    Bed.count_bed.assert_not_called()
    gc.coverage.assert_called_once_with(bed, cov, genome, sample, scale, None, ())
    Bed.bedgraph_to_bigwig.assert_called_once_with(cov, bw, genome)


def test_genome_coverage_spikesuffix(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    cov = sample + '-cov.bed'
    bw = sample + '-cov.bw'
    genome = 'human.sizes'
    spike_suffix = '-pombe'
    spiked = sample + spike_suffix + '.bed'
    count = 2000000
    spiked_count = 400000
    scale = BASE_SCALE * spiked_count / count
    Bed.count_bed = MagicMock(side_effect=[count, spiked_count])
    gc.coverage = MagicMock()
    Bed.bedgraph_to_bigwig = MagicMock()
    gc.genome_coverage(sample, genome, spike_suffix=spike_suffix)
    Bed.count_bed.assert_any_call(bed)
    Bed.count_bed.assert_any_call(spiked)
    gc.coverage.assert_called_once_with(bed, cov, genome, sample, scale, None, ())
    Bed.bedgraph_to_bigwig.assert_called_once_with(cov, bw, genome)


def test_genome_coverage_controlsuffix(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    cov = sample + '-cov.bed'
    bw = sample + '-cov.bw'
    genome = 'human.sizes'
    control_suffix = '-input'
    control = sample + control_suffix + '.bed'
    count = 2000000
    control_count = 300000
    scale = BASE_SCALE / (count * control_count)
    Bed.count_bed = MagicMock(side_effect=[count, control_count])
    gc.coverage = MagicMock()
    Bed.bedgraph_to_bigwig = MagicMock()
    gc.genome_coverage(sample, genome, control_suffix=control_suffix)
    Bed.count_bed.assert_any_call(bed)
    Bed.count_bed.assert_any_call(control)
    gc.coverage.assert_called_once_with(bed, cov, genome, sample, scale, None, ())
    Bed.bedgraph_to_bigwig.assert_called_once_with(cov, bw, genome)


def test_genome_coverage_spikeandcontrolsuffix(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    cov = sample + '-cov.bed'
    bw = sample + '-cov.bw'
    genome = 'human.sizes'
    spike_suffix = '-pombe'
    spiked = sample + spike_suffix + '.bed'
    control_suffix = '-input'
    control = sample + control_suffix + '.bed'
    count = 2000000
    spiked_count = 400000
    control_count = 300000
    scale = BASE_SCALE * spiked_count / (count * control_count)
    Bed.count_bed = MagicMock(side_effect=[count, spiked_count, control_count])
    gc.coverage = MagicMock()
    Bed.bedgraph_to_bigwig = MagicMock()
    gc.genome_coverage(sample, genome, spike_suffix=spike_suffix, control_suffix=control_suffix)
    Bed.count_bed.assert_any_call(bed)
    Bed.count_bed.assert_any_call(spiked)
    Bed.count_bed.assert_any_call(control)
    gc.coverage.assert_called_once_with(bed, cov, genome, sample, scale, None, ())
    Bed.bedgraph_to_bigwig.assert_called_once_with(cov, bw, genome)


def test_genome_coverage_scale_and_spikesuffix(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    cov = sample + '-cov.bed'
    bw = sample + '-cov.bw'
    genome = 'human.sizes'
    spike_suffix = '-pombe'
    spiked = sample + spike_suffix + '.bed'
    count = 2000000
    spiked_count = 400000
    scale = BASE_SCALE * spiked_count / count
    Bed.count_bed = MagicMock(side_effect=[count, spiked_count])
    gc.coverage = MagicMock()
    Bed.bedgraph_to_bigwig = MagicMock()
    gc.genome_coverage(sample, genome, scale=1.5, spike_suffix=spike_suffix)
    Bed.count_bed.assert_any_call(bed)
    Bed.count_bed.assert_any_call(spiked)
    gc.coverage.assert_called_once_with(bed, cov, genome, sample, scale, None, ())
    Bed.bedgraph_to_bigwig.assert_called_once_with(cov, bw, genome)


def test_genome_coverage_scale_and_controlsuffix(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    cov = sample + '-cov.bed'
    bw = sample + '-cov.bw'
    genome = 'human.sizes'
    control_suffix = '-input'
    control = sample + control_suffix + '.bed'
    count = 2000000
    control_count = 300000
    scale = BASE_SCALE / (count * control_count)
    Bed.count_bed = MagicMock(side_effect=[count, control_count])
    gc.coverage = MagicMock()
    Bed.bedgraph_to_bigwig = MagicMock()
    gc.genome_coverage(sample, genome, scale=1.5, control_suffix=control_suffix)
    Bed.count_bed.assert_any_call(bed)
    Bed.count_bed.assert_any_call(control)
    gc.coverage.assert_called_once_with(bed, cov, genome, sample, scale, None, ())
    Bed.bedgraph_to_bigwig.assert_called_once_with(cov, bw, genome)


def test_genome_coverage_negativestrand(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    cov = sample + '-cov-neg.bed'
    bw = sample + '-cov-neg.bw'
    genome = 'human.sizes'
    strand = '-'
    count = 2000000
    Bed.count_bed = MagicMock(return_value=count)
    gc.coverage = MagicMock()
    Bed.bedgraph_to_bigwig = MagicMock()
    gc.genome_coverage(sample, genome, scale=None, strand=strand)
    Bed.count_bed.assert_called_once_with(bed)
    gc.coverage.assert_called_once_with(bed, cov, genome, sample, BASE_SCALE / count, strand, ())
    Bed.bedgraph_to_bigwig.assert_called_once_with(cov, bw, genome)


def test_genome_coverage_negativestrand_suffix(testdir, mock_testclass):
    sample = 'POLR2A'
    input_suffix = '-forcov'
    output_suffix = '-outcov'
    bed = sample + input_suffix + '.bed'
    cov = sample + output_suffix + '-neg.bed'
    bw = sample + output_suffix + '-neg.bw'
    genome = 'human.sizes'
    strand = '-'
    count = 2000000
    Bed.count_bed = MagicMock(return_value=count)
    gc.coverage = MagicMock()
    Bed.bedgraph_to_bigwig = MagicMock()
    gc.genome_coverage(sample, genome, scale=None, strand=strand, input_suffix=input_suffix, output_suffix=output_suffix)
    Bed.count_bed.assert_called_once_with(bed)
    gc.coverage.assert_called_once_with(bed, cov, genome, sample, BASE_SCALE / count, strand, ())
    Bed.bedgraph_to_bigwig.assert_called_once_with(cov, bw, genome)


def test_genome_coverage_scale_negativestrand(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    cov = sample + '-cov-neg.bed'
    bw = sample + '-cov-neg.bw'
    genome = 'human.sizes'
    scale = 1.5
    strand = '-'
    Bed.count_bed = MagicMock()
    gc.coverage = MagicMock()
    Bed.bedgraph_to_bigwig = MagicMock()
    gc.genome_coverage(sample, genome, scale=scale, strand=strand)
    Bed.count_bed.assert_not_called()
    gc.coverage.assert_called_once_with(bed, cov, genome, sample, scale, strand, ())
    Bed.bedgraph_to_bigwig.assert_called_once_with(cov, bw, genome)


def test_genome_coverage_positivestrand(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    cov = sample + '-cov-pos.bed'
    bw = sample + '-cov-pos.bw'
    genome = 'human.sizes'
    strand = '+'
    count = 2000000
    Bed.count_bed = MagicMock(return_value=count)
    gc.coverage = MagicMock()
    Bed.bedgraph_to_bigwig = MagicMock()
    gc.genome_coverage(sample, genome, scale=None, strand=strand)
    Bed.count_bed.assert_called_once_with(bed)
    gc.coverage.assert_called_once_with(bed, cov, genome, sample, BASE_SCALE / count, strand, ())
    Bed.bedgraph_to_bigwig.assert_called_once_with(cov, bw, genome)


def test_genome_coverage_positivestrand_suffix(testdir, mock_testclass):
    sample = 'POLR2A'
    input_suffix = '-forcov'
    output_suffix = '-outcov'
    bed = sample + input_suffix + '.bed'
    cov = sample + output_suffix + '-pos.bed'
    bw = sample + output_suffix + '-pos.bw'
    genome = 'human.sizes'
    strand = '+'
    count = 2000000
    Bed.count_bed = MagicMock(return_value=count)
    gc.coverage = MagicMock()
    Bed.bedgraph_to_bigwig = MagicMock()
    gc.genome_coverage(sample, genome, scale=None, strand=strand, input_suffix=input_suffix, output_suffix=output_suffix)
    Bed.count_bed.assert_called_once_with(bed)
    gc.coverage.assert_called_once_with(bed, cov, genome, sample, BASE_SCALE / count, strand, ())
    Bed.bedgraph_to_bigwig.assert_called_once_with(cov, bw, genome)


def test_genome_coverage_scale_positivestrand(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    cov = sample + '-cov-pos.bed'
    bw = sample + '-cov-pos.bw'
    genome = 'human.sizes'
    scale = 1.5
    strand = '+'
    Bed.count_bed = MagicMock()
    gc.coverage = MagicMock()
    Bed.bedgraph_to_bigwig = MagicMock()
    gc.genome_coverage(sample, genome, scale=scale, strand=strand)
    Bed.count_bed.assert_not_called()
    gc.coverage.assert_called_once_with(bed, cov, genome, sample, scale, strand, ())
    Bed.bedgraph_to_bigwig.assert_called_once_with(cov, bw, genome)


def test_coverage(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    output = sample + '-out.bed'
    genome = 'human.sizes'
    subprocess.run = MagicMock(side_effect=create_file)
    Bed.sort = MagicMock(side_effect=create_file_sort)
    gc.coverage(bed, output, genome, sample)
    subprocess.run.assert_called_once_with(['bedtools', 'genomecov', '-bg', '-i', bed, '-g', genome], stdout=ANY, check=True)
    Bed.sort.assert_called_once_with(ANY, ANY)
    with open(output, 'r') as infile:
        assert infile.readline() == 'track type=bedGraph name="' + sample + '"\n'
        assert infile.readline() == 'test'


def test_coverage_five(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    output = sample + '-out.bed'
    genome = 'human.sizes'
    subprocess.run = MagicMock(side_effect=create_file)
    Bed.sort = MagicMock(side_effect=create_file_sort)
    gc.coverage(bed, output, genome, sample, genomecov_args=('-5',))
    subprocess.run.assert_called_once_with(['bedtools', 'genomecov', '-bg', '-i', bed, '-g', genome, '-5'], stdout=ANY, check=True)
    Bed.sort.assert_called_once_with(ANY, ANY)
    with open(output, 'r') as infile:
        assert infile.readline() == 'track type=bedGraph name="' + sample + '"\n'
        assert infile.readline() == 'test'


def test_coverage_three(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    output = sample + '-out.bed'
    genome = 'human.sizes'
    subprocess.run = MagicMock(side_effect=create_file)
    Bed.sort = MagicMock(side_effect=create_file_sort)
    gc.coverage(bed, output, genome, sample, genomecov_args=('-3',))
    subprocess.run.assert_called_once_with(['bedtools', 'genomecov', '-bg', '-i', bed, '-g', genome, '-3'], stdout=ANY, check=True)
    Bed.sort.assert_called_once_with(ANY, ANY)
    with open(output, 'r') as infile:
        assert infile.readline() == 'track type=bedGraph name="' + sample + '"\n'
        assert infile.readline() == 'test'


def test_coverage_scale(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    output = sample + '-out.bed'
    genome = 'human.sizes'
    scale = 1.5
    subprocess.run = MagicMock(side_effect=create_file)
    Bed.sort = MagicMock(side_effect=create_file_sort)
    gc.coverage(bed, output, genome, sample, scale)
    subprocess.run.assert_called_once_with(['bedtools', 'genomecov', '-bg', '-i', bed, '-g', genome, '-scale', str(scale)], stdout=ANY, check=True)
    Bed.sort.assert_called_once_with(ANY, ANY)
    with open(output, 'r') as infile:
        assert infile.readline() == 'track type=bedGraph name="' + sample + '"\n'
        assert infile.readline() == 'test'


def test_coverage_negativestrand(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    output = sample + '-out.bed'
    genome = 'human.sizes'
    strand = '-'
    subprocess.run = MagicMock(side_effect=create_file)
    Bed.sort = MagicMock(side_effect=create_file_sort)
    gc.coverage(bed, output, genome, sample, None, strand)
    subprocess.run.assert_called_once_with(['bedtools', 'genomecov', '-bg', '-i', bed, '-g', genome, '-strand', strand], stdout=ANY, check=True)
    Bed.sort.assert_called_once_with(ANY, ANY)
    with open(output, 'r') as infile:
        assert infile.readline() == 'track type=bedGraph name="' + sample + ' Minus"\n'
        assert infile.readline() == 'test'


def test_coverage_scale_negativestrand(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    output = sample + '-out.bed'
    genome = 'human.sizes'
    scale = 1.5
    strand = '-'
    subprocess.run = MagicMock(side_effect=create_file)
    Bed.sort = MagicMock(side_effect=create_file_sort)
    gc.coverage(bed, output, genome, sample, scale, strand)
    subprocess.run.assert_called_once_with(['bedtools', 'genomecov', '-bg', '-i', bed, '-g', genome, '-scale', str(scale), '-strand', strand], stdout=ANY, check=True)
    Bed.sort.assert_called_once_with(ANY, ANY)
    with open(output, 'r') as infile:
        assert infile.readline() == 'track type=bedGraph name="' + sample + ' Minus"\n'
        assert infile.readline() == 'test'


def test_coverage_positivestrand(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    output = sample + '-out.bed'
    genome = 'human.sizes'
    strand = '+'
    subprocess.run = MagicMock(side_effect=create_file)
    Bed.sort = MagicMock(side_effect=create_file_sort)
    gc.coverage(bed, output, genome, sample, None, strand)
    subprocess.run.assert_called_once_with(['bedtools', 'genomecov', '-bg', '-i', bed, '-g', genome, '-strand', strand], stdout=ANY, check=True)
    Bed.sort.assert_called_once_with(ANY, ANY)
    with open(output, 'r') as infile:
        assert infile.readline() == 'track type=bedGraph name="' + sample + ' Plus"\n'
        assert infile.readline() == 'test'


def test_coverage_scale_positivestrand(testdir, mock_testclass):
    sample = 'POLR2A'
    bed = sample + '.bed'
    output = sample + '-out.bed'
    genome = 'human.sizes'
    scale = 1.5
    strand = '+'
    subprocess.run = MagicMock(side_effect=create_file)
    Bed.sort = MagicMock(side_effect=create_file_sort)
    gc.coverage(bed, output, genome, sample, scale, strand)
    subprocess.run.assert_called_once_with(['bedtools', 'genomecov', '-bg', '-i', bed, '-g', genome, '-scale', str(scale), '-strand', strand], stdout=ANY, check=True)
    Bed.sort.assert_called_once_with(ANY, ANY)
    with open(output, 'r') as infile:
        assert infile.readline() == 'track type=bedGraph name="' + sample + ' Plus"\n'
        assert infile.readline() == 'test'
