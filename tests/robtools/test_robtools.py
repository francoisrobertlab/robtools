import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from robtools import Bam2Bed
from robtools import Bowtie2
from robtools import Bwa
from robtools import CenterAnnotations
from robtools import ChipexoQual
from robtools import Download
from robtools import FilterBam
from robtools import Fixmd5
from robtools import GenomeCoverage
from robtools import IgnoreStrand
from robtools import Intersect
from robtools import KeepRandomReads
from robtools import Merge
from robtools import MergeBam
from robtools import MergeBigwigs
from robtools import Pairs2Hic
from robtools import Plot2do
from robtools import PrintSample
from robtools import RemoveSecondMate
from robtools import Rename
from robtools import ShiftAnnotations
from robtools import Siqchip
from robtools import SiqchipBed
from robtools import SlowSplit
from robtools import Split
from robtools import Statistics
from robtools import Trimmomatic
from robtools import Vap
from robtools import robtools


@pytest.fixture
def mock_testclass():
    bam2bed_samples = Bam2Bed.bam2bed_samples
    bowtie_samples = Bowtie2.bowtie_samples
    bwa_samples = Bwa.bwa_samples
    center_annotations_samples = CenterAnnotations.center_annotations_samples
    chipexoqual_datasets = ChipexoQual.chipexoqual_datasets
    download_samples = Download.download_samples
    filter_bam = FilterBam.filter_bam
    fixmd5 = Fixmd5.fixmd5_
    genome_coverage_samples = GenomeCoverage.genome_coverage_samples
    ignore_strand_samples = IgnoreStrand.ignore_strand_samples
    intersect_samples = Intersect.intersect_samples
    keeprandomreads_samples = KeepRandomReads.keeprandomreads_samples
    merge_datasets = Merge.merge_datasets
    merge_datasets_bam = MergeBam.merge_datasets
    merge_datasets_bw = MergeBigwigs.merge_datasets
    pairs2hic = Pairs2Hic.pairs2hic
    plot2do_samples = Plot2do.plot2do_samples
    print_sample = PrintSample.print_sample
    removesecondmate_samples = RemoveSecondMate.removesecondmate_samples
    rename = Rename.rename_
    shift_annotations_samples = ShiftAnnotations.shift_annotations_samples
    siqchip_samples = Siqchip.siqchip_samples
    siqchipbed_samples = SiqchipBed.siqchipbed_samples
    slow_split_samples = SlowSplit.split_samples
    split_samples = Split.split_samples
    statistics_samples = Statistics.statistics_samples
    trimmomatic_samples = Trimmomatic.trimmomatic_samples
    vap_samples = Vap.vap_samples
    yield
    Bam2Bed.bam2bed_samples = bam2bed_samples
    Bowtie2.bowtie_samples = bowtie_samples
    Bwa.bwa_samples = bwa_samples
    CenterAnnotations.center_annotations_samples = center_annotations_samples
    ChipexoQual.chipexoqual_datasets = chipexoqual_datasets
    Download.download_samples = download_samples
    FilterBam.filter_bam = filter_bam
    Fixmd5.fixmd5_ = fixmd5
    GenomeCoverage.genome_coverage_samples = genome_coverage_samples
    IgnoreStrand.ignore_strand_samples = ignore_strand_samples
    Intersect.intersect_samples = intersect_samples
    KeepRandomReads.keeprandomreads_samples = keeprandomreads_samples
    Merge.merge_datasets = merge_datasets
    MergeBam.merge_datasets = merge_datasets_bam
    MergeBigwigs.merge_datasets = merge_datasets_bw
    Pairs2Hic.pairs2hic = pairs2hic
    Plot2do.plot2do_samples = plot2do_samples
    PrintSample.print_sample = print_sample
    RemoveSecondMate.removesecondmate_samples = removesecondmate_samples
    Rename.rename_ = rename
    ShiftAnnotations.shift_annotations_samples = shift_annotations_samples
    Siqchip.siqchip_samples = siqchip_samples
    SiqchipBed.siqchipbed_samples = siqchipbed_samples
    SlowSplit.split_samples = slow_split_samples
    Split.split_samples = split_samples
    Statistics.statistics_samples = statistics_samples
    Trimmomatic.trimmomatic_samples = trimmomatic_samples
    Vap.vap_samples = vap_samples


def test_robtools_bam2bed(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    threads = 3
    index = 2
    Bam2Bed.bam2bed_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools,
                           ['bam2bed', '--samples', samples, '--unpaired', '--threads', threads, '--index', index])
    assert result.exit_code == 0
    Bam2Bed.bam2bed_samples.assert_called_once_with(samples, False, threads, '-dedup', '', index)


def test_robtools_bowtie2(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    threads = 3
    index = 2
    Bowtie2.bowtie_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools,
                           ['bowtie2', '--samples', samples, '--threads', threads, '--index', index, '-x',
                            'sacCer3.fa'])
    assert result.exit_code == 0
    Bowtie2.bowtie_samples.assert_called_once_with(samples, threads, '', '', index, ('-x', 'sacCer3.fa'))


def test_robtools_bwa(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    fasta = Path(__file__).parent.joinpath('sacCer3.fa')
    threads = 3
    index = 2
    Bwa.bwa_sample = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools,
                           ['bwa', '--samples', samples, '--fasta', fasta, '--threads', threads, '--index', index])
    assert result.exit_code == 0
    Bwa.bwa_sample.assert_called_once_with('POLR1C', fasta, threads, '', '', ())


def test_robtools_centerannotations(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    CenterAnnotations.center_annotations_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools, ['centerannotations', '--samples', samples])
    assert result.exit_code == 0
    CenterAnnotations.center_annotations_samples.assert_called_once_with(samples, '', '-forcov', None)


def test_robtools_chipexoqual(testdir, mock_testclass):
    datasets = Path(__file__).parent.joinpath('dataset.txt')
    ChipexoQual.chipexoqual_datasets = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools, ['chipexoqual', '--datasets', datasets])
    assert result.exit_code == 0
    ChipexoQual.chipexoqual_datasets.assert_called_once_with(datasets, '', None, ())


def test_robtools_distillerresolutions(testdir, mock_testclass):
    project = Path(__file__).parent.joinpath('project.yml')
    runner = CliRunner()
    result = runner.invoke(robtools.robtools,
                           ['distillerresolutions', '--project', project])
    logging.warning(result.output)
    assert result.exit_code == 0
    assert result.stdout == '10000\n5000\n2000\n1000\n500\n200\n100\n50\n20\n10\n'


def test_robtools_download(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    fasta = Path(__file__).parent.joinpath('sacCer3.fa')
    mem = '200MB'
    threads = 3
    index = 2
    Download.download_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools,
                           ['download', '--samples', samples, '--slow', '--threads', threads, '--mem', mem, '--index',
                            index])
    logging.warning(result.output)
    assert result.exit_code == 0
    Download.download_samples.assert_called_once_with(samples, False, threads, mem, index)


def test_robtools_filterbam(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    threads = 3
    index = 2
    FilterBam.filter_bam = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools,
                           ['filterbam', '--samples', samples, '--unpaired', '--threads', threads, '--index', index])
    assert result.exit_code == 0
    FilterBam.filter_bam.assert_called_once_with(samples, False, True, None, threads, '', '', index)


def test_robtools_fixmd5(testdir, mock_testclass):
    Fixmd5.fixmd5_ = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools, ['fixmd5'])
    assert result.exit_code == 0
    Fixmd5.fixmd5_.assert_called_once_with('*.md5', False)


def test_robtools_genomecov(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    sizes = Path(__file__).parent.joinpath('sizes.txt')
    scale = 1.5
    strand = '-'
    input_suffix = '-forcov'
    output_suffix = '-cov'
    index = 2
    GenomeCoverage.genome_coverage_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools,
                           ['genomecov', '--samples', samples, '-g', sizes, '-5', '-scale', scale, '-strand', strand,
                            '-is', input_suffix, '-os', output_suffix, '--index', index])
    assert result.exit_code == 0
    GenomeCoverage.genome_coverage_samples.assert_called_once_with(samples, sizes, scale, strand, input_suffix,
                                                                   output_suffix, None, None, None, index, ('-5',))


def test_robtools_ignorestrand(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    IgnoreStrand.ignore_strand_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools, ['ignorestrand', '--samples', samples])
    assert result.exit_code == 0
    IgnoreStrand.ignore_strand_samples.assert_called_once_with(samples, '', '-forcov', None)


def test_robtools_intersect(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('intersect.txt')
    annotations = Path(__file__).parent.joinpath('annotations.bed')
    index = 2
    Intersect.intersect_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools,
                           ['intersect', '--samples', samples, '--annotations', annotations, '--index', index])
    assert result.exit_code == 0
    Intersect.intersect_samples.assert_called_once_with(samples, annotations, index)


def test_robtools_keeprandomreads(mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    KeepRandomReads.keeprandomreads_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools, ['keeprandomreads', '--samples', samples])
    logging.warning(result.output)
    assert result.exit_code == 0
    KeepRandomReads.keeprandomreads_samples.assert_called_once_with(samples, 10000000, True, 1, '', '-random', None)


def test_robtools_merge(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('dataset.txt')
    index = 2
    Merge.merge_datasets = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools, ['merge', '--datasets', samples, '--index', index])
    logging.warning(result.output)
    assert result.exit_code == 0
    Merge.merge_datasets.assert_called_once_with(samples, index)


def test_robtools_mergebam(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('dataset.txt')
    index = 2
    MergeBam.merge_datasets = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools, ['mergebam', '--datasets', samples])
    logging.warning(result.output)
    assert result.exit_code == 0
    MergeBam.merge_datasets.assert_called_once_with(samples, '', 1, None)


def test_robtools_mergebw(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('dataset.txt')
    sizes = Path(__file__).parent.joinpath('sizes.txt')
    index = 2
    MergeBigwigs.merge_datasets = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools, ['mergebw', '--datasets', samples, '--sizes', sizes, '--index', index])
    logging.warning(result.output)
    assert result.exit_code == 0
    MergeBigwigs.merge_datasets.assert_called_once_with(samples, sizes, index)


def test_robtools_pairs2hic(testdir, mock_testclass):
    project = Path(__file__).parent.joinpath('project.yml')
    juicer = "juicer_tools.jar"
    Path(juicer).touch()
    Pairs2Hic.pairs2hic_ = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools, ['pairs2hic', '--project', project])
    logging.warning(result.output)
    assert result.exit_code == 0
    Pairs2Hic.pairs2hic_.assert_called_once_with(project, juicer, "*.nodups", None, None, ())


def test_robtools_plot2do(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    index = 2
    type = 'dyads'
    Plot2do.plot2do_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools, ['plot2do', '--file', samples, '--type', type, '--index', index])
    logging.warning(result.output)
    assert result.exit_code == 0
    Plot2do.plot2do_samples.assert_called_once_with(samples, '', index, ('--type', type,))


def test_robtools_printsample(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    index = 1
    PrintSample.print_sample = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools, ['printsample', '--samples', samples, '--index', index])
    logging.warning(result.output)
    assert result.exit_code == 0
    PrintSample.print_sample.assert_called_once_with(samples, False, '', index)


def test_robtools_removesecondmate(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    RemoveSecondMate.removesecondmate_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools, ['removesecondmate', '--samples', samples])
    assert result.exit_code == 0
    RemoveSecondMate.removesecondmate_samples.assert_called_once_with(samples, '-dedup', '-mate1', 1, None)


def test_robtools_rename(testdir, mock_testclass):
    names = Path(__file__).parent.joinpath('names.txt')
    Rename.rename_ = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools, ['rename', '--names', names])
    logging.warning(result.output)
    assert result.exit_code == 0
    Rename.rename_.assert_called_once_with(names, True, False, False)


def test_robtools_shiftannotations(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    ShiftAnnotations.shift_annotations_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools, ['shiftannotations', '--samples', samples])
    assert result.exit_code == 0
    ShiftAnnotations.shift_annotations_samples.assert_called_once_with(samples, '', '-forcov', None, ())


def test_robtools_siqchip(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    sizes = Path(__file__).parent.joinpath('sizes.txt')
    resi = Path(__file__).parent.joinpath('siqchip-resi.txt')
    Siqchip.siqchip_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools,
                           ['siqchip', '--samples', samples, '--chromosomes', sizes, '--resolution', resi])
    assert result.exit_code == 0
    Siqchip.siqchip_samples.assert_called_once_with(samples, sizes, resi, '-input-reads', '-reads', '-params',
                                                    '-siqchip', 1, None)


def test_robtools_siqchipbed(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    SiqchipBed.siqchipbed_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools, ['siqchipbed', '--samples', samples])
    assert result.exit_code == 0
    SiqchipBed.siqchipbed_samples.assert_called_once_with(samples, '-dedup', '-reads', None, None)


def test_robtools_slowsplit(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    binlength = 20
    binminlength = 50
    binmaxlength = 150
    index = 2
    SlowSplit.split_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools,
                           ['slowsplit', '--samples', samples, '--binLength', binlength, '--binMinLength', binminlength,
                            '--binMaxLength', binmaxlength, '--index', index])
    logging.warning(result.output)
    assert result.exit_code == 0
    SlowSplit.split_samples.assert_called_once_with(samples, index, binlength, binminlength, binmaxlength)


def test_robtools_split(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    binlength = 20
    binminlength = 50
    binmaxlength = 150
    index = 2
    Split.split_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools,
                           ['split', '--samples', samples, '--binLength', binlength, '--binMinLength', binminlength,
                            '--binMaxLength', binmaxlength, '--index', index])
    logging.warning(result.output)
    assert result.exit_code == 0
    Split.split_samples.assert_called_once_with(samples, index, binlength, binminlength, binmaxlength)


def test_robtools_statistics(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    datasets = Path(__file__).parent.joinpath('dataset.txt')
    output = 'stats.txt'
    Statistics.statistics_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools,
                           ['statistics', '--samples', samples, '--datasets', datasets, '--output', output])
    logging.warning(result.output)
    assert result.exit_code == 0
    Statistics.statistics_samples.assert_called_once_with(samples, datasets, '', '-filtered', '', False, output)


def test_robtools_trimmomatic(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    Trimmomatic.trimmomatic_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools, ['trimmomatic', '--samples', samples])
    logging.warning(result.output)
    assert result.exit_code == 0
    Trimmomatic.trimmomatic_samples.assert_called_once_with(samples, '', '-trim', '-paired', '-unpaired', None, None,
                                                            ())


def test_robtools_vap(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    parameters = Path(__file__).parent.joinpath('parameters.txt')
    index = 2
    Vap.vap_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(robtools.robtools,
                           ['vap', '--samples', samples, '--parameters', parameters, '--index', index])
    logging.warning(result.output)
    assert result.exit_code == 0
    Vap.vap_samples.assert_called_once_with(samples, parameters, None, index)
