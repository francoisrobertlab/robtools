import os
import subprocess
from pathlib import Path
from shutil import copyfile
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from robtools import Trimmomatic as t
from robtools.Trimmomatic import SBATCH_JAVA_MEM_ENV
from robtools.Trimmomatic import TRIMMOMATIC_ADAPTERS_ENV
from robtools.Trimmomatic import TRIMMOMATIC_JAR_ENV
from robtools.seq import Fastq


@pytest.fixture
def mock_testclass():
    trimmomatic_samples = t.trimmomatic_samples
    trimmomatic_sample = t.trimmomatic_sample
    trimmomatic_single = t.trimmomatic_single
    trimmomatic_paired = t.trimmomatic_paired
    sbatch_memory = t.sbatch_memory
    fastq = Fastq.fastq
    run = subprocess.run
    yield
    t.trimmomatic_samples = trimmomatic_samples
    t.trimmomatic_sample = trimmomatic_sample
    t.trimmomatic_single = trimmomatic_single
    t.trimmomatic_paired = trimmomatic_paired
    t.sbatch_memory = sbatch_memory
    Fastq.fastq = fastq
    subprocess.run = run
    if SBATCH_JAVA_MEM_ENV in os.environ:
        del os.environ[SBATCH_JAVA_MEM_ENV]
    if TRIMMOMATIC_ADAPTERS_ENV in os.environ:
        del os.environ[TRIMMOMATIC_ADAPTERS_ENV]
    if TRIMMOMATIC_JAR_ENV in os.environ:
        del os.environ[TRIMMOMATIC_JAR_ENV]


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


def test_trimmomatic(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    t.trimmomatic_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(t.trimmomatic, ['--samples', samples])
    assert result.exit_code == 0
    t.trimmomatic_samples.assert_called_once_with(samples, '', '-trim', '-paired', '-unpaired', None, None, ())


def test_trimmomatic_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    input_suffix = '-in'
    output_suffix = '-out'
    paired_suffix = '-par'
    unpaired_suffix = '-upar'
    trimmers = 'ILLUMINACLIP:TruSeq3-PE-2.fa:2:30:10:2:keepBothReads MINLEN:36'
    index = 1
    t.trimmomatic_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(t.trimmomatic, ['--samples', samples, '-trimlog', 'trimlog', '--input-suffix', input_suffix,
                                           '--output-suffix', output_suffix, '--paired-suffix', paired_suffix,
                                           '--unpaired-suffix', unpaired_suffix, '--trimmers', trimmers, '--index',
                                           index])
    assert result.exit_code == 0
    t.trimmomatic_samples.assert_called_once_with(samples, input_suffix, output_suffix, paired_suffix, unpaired_suffix,
                                                  trimmers, index, ('-trimlog', 'trimlog',))


def test_trimmomatic_filenotexists(testdir, mock_testclass):
    samples = 'samples.txt'
    t.trimmomatic_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(t.trimmomatic, ['--samples', samples])
    assert result.exit_code != 0
    t.trimmomatic_samples.assert_not_called()


def test_trimmomatic_samples(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    t.trimmomatic_sample = MagicMock()
    t.trimmomatic_samples(samples)
    t.trimmomatic_sample.assert_any_call('POLR2A', '', '-trim', '-paired', '-unpaired', None, ())
    t.trimmomatic_sample.assert_any_call('ASDURF', '', '-trim', '-paired', '-unpaired', None, ())
    t.trimmomatic_sample.assert_any_call('POLR1C', '', '-trim', '-paired', '-unpaired', None, ())


def test_trimmomatic_samples_second(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    t.trimmomatic_sample = MagicMock()
    t.trimmomatic_samples(samples, index=1)
    t.trimmomatic_sample.assert_called_once_with('ASDURF', '', '-trim', '-paired', '-unpaired', None, ())


def test_trimmomatic_samples_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    input_suffix = '-in'
    output_suffix = '-out'
    paired_suffix = '-par'
    unpaired_suffix = '-upar'
    trimmers = 'ILLUMINACLIP:TruSeq3-PE-2.fa:2:30:10:2:keepBothReads MINLEN:36'
    trim_args = ('-trimlog', 'trim.log',)
    t.trimmomatic_sample = MagicMock()
    t.trimmomatic_samples(samples, input_suffix, output_suffix, paired_suffix, unpaired_suffix, trimmers,
                          trim_args=trim_args)
    t.trimmomatic_sample.assert_any_call('POLR2A', input_suffix, output_suffix, paired_suffix, unpaired_suffix,
                                         trimmers, trim_args)
    t.trimmomatic_sample.assert_any_call('ASDURF', input_suffix, output_suffix, paired_suffix, unpaired_suffix,
                                         trimmers, trim_args)
    t.trimmomatic_sample.assert_any_call('POLR1C', input_suffix, output_suffix, paired_suffix, unpaired_suffix,
                                         trimmers, trim_args)


def test_trimmomatic_sample_single(testdir, mock_testclass):
    sample = 'PORL2A'
    fastq = sample + '_1.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq)
    output = sample + '-trim_1.fastq'
    t.trimmomatic_single = MagicMock()
    t.trimmomatic_paired = MagicMock()
    Fastq.fastq = MagicMock(side_effect=[fastq, None])
    t.trimmomatic_sample(sample)
    Fastq.fastq.assert_any_call(sample, 1)
    Fastq.fastq.assert_any_call(sample, 2)
    t.trimmomatic_single.assert_called_once_with(fastq, output, None, ())
    t.trimmomatic_paired.assert_not_called()


def test_trimmomatic_sample_singlegz(testdir, mock_testclass):
    sample = 'PORL2A'
    fastq = sample + '_1.fastq.gz'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq)
    output = sample + '-trim_1.fastq.gz'
    t.trimmomatic_single = MagicMock()
    t.trimmomatic_paired = MagicMock()
    Fastq.fastq = MagicMock(side_effect=[fastq, None])
    t.trimmomatic_sample(sample)
    Fastq.fastq.assert_any_call(sample, 1)
    Fastq.fastq.assert_any_call(sample, 2)
    t.trimmomatic_single.assert_called_once_with(fastq, output, None, ())
    t.trimmomatic_paired.assert_not_called()


def test_trimmomatic_sample_singleparameters(testdir, mock_testclass):
    sample = 'PORL2A'
    input_suffix = '-in'
    output_suffix = '-out'
    paired_suffix = '-par'
    unpaired_suffix = '-upar'
    trimmers = 'ILLUMINACLIP:TruSeq3-PE-2.fa:2:30:10:2:keepBothReads MINLEN:36'
    trim_args = ('-trimlog', 'trim.log',)
    fastq = sample + input_suffix + '_1.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq)
    output = sample + output_suffix + '_1.fastq'
    t.trimmomatic_single = MagicMock()
    t.trimmomatic_paired = MagicMock()
    Fastq.fastq = MagicMock(side_effect=[fastq, None])
    t.trimmomatic_sample(sample, input_suffix, output_suffix, paired_suffix, unpaired_suffix, trimmers, trim_args)
    Fastq.fastq.assert_any_call(sample + input_suffix, 1)
    Fastq.fastq.assert_any_call(sample + input_suffix, 2)
    t.trimmomatic_single.assert_called_once_with(fastq, output,
                                                 ['ILLUMINACLIP:TruSeq3-PE-2.fa:2:30:10:2:keepBothReads', 'MINLEN:36'],
                                                 trim_args)
    t.trimmomatic_paired.assert_not_called()


def test_trimmomatic_sample_singleillumina(testdir, mock_testclass):
    adapters = 'adapters'
    os.environ[TRIMMOMATIC_ADAPTERS_ENV] = adapters
    os.mkdir(adapters)
    Path(adapters + '/TruSeq3-PE-2.fa').touch()
    Path(adapters + '/TruSeq2-PE.fa').touch()
    sample = 'PORL2A'
    trimmers = 'ILLUMINACLIP:TruSeq3-PE-2.fa:2:30:10:2:keepBothReads MINLEN:36 ILLUMINACLIP:TruSeq3-PE.fa:2:30:10 ILLUMINACLIP:TruSeq2-PE.fa:2:30:10'
    fastq = sample + '_1.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq)
    output = sample + '-trim_1.fastq'
    t.trimmomatic_single = MagicMock()
    t.trimmomatic_paired = MagicMock()
    Fastq.fastq = MagicMock(side_effect=[fastq, None])
    t.trimmomatic_sample(sample, trimmers=trimmers)
    Fastq.fastq.assert_any_call(sample, 1)
    Fastq.fastq.assert_any_call(sample, 2)
    t.trimmomatic_single.assert_called_once_with(fastq, output,
                                                 ['ILLUMINACLIP:adapters/TruSeq3-PE-2.fa:2:30:10:2:keepBothReads',
                                                  'MINLEN:36', 'ILLUMINACLIP:TruSeq3-PE.fa:2:30:10',
                                                  'ILLUMINACLIP:adapters/TruSeq2-PE.fa:2:30:10'], ())
    t.trimmomatic_paired.assert_not_called()


def test_trimmomatic_sample_paired(testdir, mock_testclass):
    sample = 'PORL2A'
    fastq1 = sample + '_1.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq1)
    paired1 = sample + '-paired_1.fastq'
    unpaired1 = sample + '-unpaired_1.fastq'
    fastq2 = sample + '_2.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq2)
    paired2 = sample + '-paired_2.fastq'
    unpaired2 = sample + '-unpaired_2.fastq'
    t.trimmomatic_paired = MagicMock()
    t.trimmomatic_single = MagicMock()
    Fastq.fastq = MagicMock(side_effect=[fastq1, fastq2])
    t.trimmomatic_sample(sample)
    Fastq.fastq.assert_any_call(sample, 1)
    Fastq.fastq.assert_any_call(sample, 2)
    t.trimmomatic_paired.assert_called_once_with(fastq1, paired1, unpaired1, fastq2, paired2, unpaired2, None, ())
    t.trimmomatic_single.assert_not_called()


def test_trimmomatic_sample_pairedgz(testdir, mock_testclass):
    sample = 'PORL2A'
    fastq1 = sample + '_1.fastq.gz'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq1)
    paired1 = sample + '-paired_1.fastq.gz'
    unpaired1 = sample + '-unpaired_1.fastq.gz'
    fastq2 = sample + '_2.fastq.gz'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq2)
    paired2 = sample + '-paired_2.fastq.gz'
    unpaired2 = sample + '-unpaired_2.fastq.gz'
    t.trimmomatic_paired = MagicMock()
    t.trimmomatic_single = MagicMock()
    Fastq.fastq = MagicMock(side_effect=[fastq1, fastq2])
    t.trimmomatic_sample(sample)
    Fastq.fastq.assert_any_call(sample, 1)
    Fastq.fastq.assert_any_call(sample, 2)
    t.trimmomatic_paired.assert_called_once_with(fastq1, paired1, unpaired1, fastq2, paired2, unpaired2, None, ())
    t.trimmomatic_single.assert_not_called()


def test_trimmomatic_sample_pairedparameters(testdir, mock_testclass):
    sample = 'PORL2A'
    input_suffix = '-in'
    output_suffix = '-out'
    paired_suffix = '-par'
    unpaired_suffix = '-upar'
    trimmers = 'ILLUMINACLIP:TruSeq3-PE-2.fa:2:30:10:2:keepBothReads MINLEN:36'
    trim_args = ('-trimlog', 'trim.log',)
    fastq1 = sample + input_suffix + '_1.fastq.gz'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq1)
    paired1 = sample + paired_suffix + '_1.fastq.gz'
    unpaired1 = sample + unpaired_suffix + '_1.fastq.gz'
    fastq2 = sample + input_suffix + '_2.fastq.gz'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq2)
    paired2 = sample + paired_suffix + '_2.fastq.gz'
    unpaired2 = sample + unpaired_suffix + '_2.fastq.gz'
    t.trimmomatic_paired = MagicMock()
    t.trimmomatic_single = MagicMock()
    Fastq.fastq = MagicMock(side_effect=[fastq1, fastq2])
    t.trimmomatic_sample(sample, input_suffix, output_suffix, paired_suffix, unpaired_suffix, trimmers, trim_args)
    Fastq.fastq.assert_any_call(sample + input_suffix, 1)
    Fastq.fastq.assert_any_call(sample + input_suffix, 2)
    t.trimmomatic_paired.assert_called_once_with(fastq1, paired1, unpaired1, fastq2, paired2, unpaired2,
                                                 ['ILLUMINACLIP:TruSeq3-PE-2.fa:2:30:10:2:keepBothReads', 'MINLEN:36'],
                                                 trim_args)
    t.trimmomatic_single.assert_not_called()


def test_trimmomatic_sample_pairedillumina(testdir, mock_testclass):
    adapters = 'adapters'
    os.environ[TRIMMOMATIC_ADAPTERS_ENV] = adapters
    os.mkdir(adapters)
    Path(adapters + '/TruSeq3-PE-2.fa').touch()
    Path(adapters + '/TruSeq2-PE.fa').touch()
    sample = 'PORL2A'
    trimmers = 'ILLUMINACLIP:TruSeq3-PE-2.fa:2:30:10:2:keepBothReads MINLEN:36 ILLUMINACLIP:TruSeq3-PE.fa:2:30:10 ILLUMINACLIP:TruSeq2-PE.fa:2:30:10'
    fastq1 = sample + '_1.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq1)
    paired1 = sample + '-paired_1.fastq'
    unpaired1 = sample + '-unpaired_1.fastq'
    fastq2 = sample + '_2.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq2)
    paired2 = sample + '-paired_2.fastq'
    unpaired2 = sample + '-unpaired_2.fastq'
    t.trimmomatic_paired = MagicMock()
    t.trimmomatic_single = MagicMock()
    Fastq.fastq = MagicMock(side_effect=[fastq1, fastq2])
    t.trimmomatic_sample(sample, trimmers=trimmers)
    Fastq.fastq.assert_any_call(sample, 1)
    Fastq.fastq.assert_any_call(sample, 2)
    t.trimmomatic_paired.assert_called_once_with(fastq1, paired1, unpaired1, fastq2, paired2, unpaired2,
                                                 ['ILLUMINACLIP:adapters/TruSeq3-PE-2.fa:2:30:10:2:keepBothReads',
                                                  'MINLEN:36', 'ILLUMINACLIP:TruSeq3-PE.fa:2:30:10',
                                                  'ILLUMINACLIP:adapters/TruSeq2-PE.fa:2:30:10'], ())
    t.trimmomatic_single.assert_not_called()


def test_trimmomatic_single(testdir, mock_testclass):
    jar = 'trimmomatic/trimmomatic.jar'
    os.environ[TRIMMOMATIC_JAR_ENV] = jar
    sample = 'PORL2A'
    fastq = sample + '_1.fastq'
    output = sample + '-trim_1.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq)
    subprocess.run = MagicMock()
    t.trimmomatic_single(fastq, output, None, ())
    subprocess.run.assert_any_call(['java', '-jar', jar, 'SE', fastq, output], check=True)


def test_trimmomatic_single_parameters(testdir, mock_testclass):
    jar = 'trimmomatic/trimmomatic.jar'
    os.environ[TRIMMOMATIC_JAR_ENV] = jar
    sample = 'PORL2A'
    fastq = sample + '_1.fastq'
    output = sample + '-trim_1.fastq'
    trimmers = ['ILLUMINACLIP:TruSeq3-PE-2.fa:2:30:10:2:keepBothReads', 'MINLEN:36']
    trim_args = ('-trimlog', 'trim.log',)
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq)
    subprocess.run = MagicMock()
    t.trimmomatic_single(fastq, output, trimmers, trim_args)
    subprocess.run.assert_any_call(['java', '-jar', jar, 'SE', '-trimlog', 'trim.log', fastq, output,
                                    'ILLUMINACLIP:TruSeq3-PE-2.fa:2:30:10:2:keepBothReads', 'MINLEN:36'], check=True)


def test_trimmomatic_single_nojarenv(testdir, mock_testclass):
    sample = 'PORL2A'
    fastq = sample + '_1.fastq'
    output = sample + '-trim_1.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq)
    subprocess.run = MagicMock()
    t.trimmomatic_single(fastq, output, None, ())
    subprocess.run.assert_any_call(['java', '-jar', 'trimmomatic.jar', 'SE', fastq, output], check=True)


def test_trimmomatic_single_sbatchmemenv(testdir, mock_testclass):
    jar = 'trimmomatic/trimmomatic.jar'
    os.environ[TRIMMOMATIC_JAR_ENV] = jar
    mem = '48G'
    os.environ[SBATCH_JAVA_MEM_ENV] = mem
    sample = 'PORL2A'
    fastq = sample + '_1.fastq'
    output = sample + '-trim_1.fastq'
    copyfile(Path(__file__).parent.joinpath('samples.txt'), fastq)
    subprocess.run = MagicMock()
    t.trimmomatic_single(fastq, output, None, ())
    subprocess.run.assert_any_call(['java', '-Xmx49152M', '-jar', jar, 'SE', fastq, output], check=True)


def test_trimmomatic_paired(testdir, mock_testclass):
    jar = 'trimmomatic/trimmomatic.jar'
    os.environ[TRIMMOMATIC_JAR_ENV] = jar
    sample = 'PORL2A'
    fastq1 = sample + '_1.fastq'
    paired1 = sample + '-paired_1.fastq'
    unpaired1 = sample + '-unpaired_1.fastq'
    fastq2 = sample + '_2.fastq'
    paired2 = sample + '-paired_2.fastq'
    unpaired2 = sample + '-unpaired_2.fastq'
    subprocess.run = MagicMock()
    t.trimmomatic_paired(fastq1, paired1, unpaired1, fastq2, paired2, unpaired2, None, ())
    subprocess.run.assert_any_call(['java', '-jar', jar, 'PE', fastq1, fastq2, paired1, unpaired1, paired2, unpaired2],
                                   check=True)


def test_trimmomatic_paired_parameters(testdir, mock_testclass):
    jar = 'trimmomatic/trimmomatic.jar'
    os.environ[TRIMMOMATIC_JAR_ENV] = jar
    sample = 'PORL2A'
    fastq1 = sample + '_1.fastq'
    paired1 = sample + '-paired_1.fastq'
    unpaired1 = sample + '-unpaired_1.fastq'
    fastq2 = sample + '_2.fastq'
    paired2 = sample + '-paired_2.fastq'
    unpaired2 = sample + '-unpaired_2.fastq'
    trimmers = ['ILLUMINACLIP:TruSeq3-PE-2.fa:2:30:10:2:keepBothReads', 'MINLEN:36']
    trim_args = ('-trimlog', 'trim.log',)
    subprocess.run = MagicMock()
    t.trimmomatic_paired(fastq1, paired1, unpaired1, fastq2, paired2, unpaired2, trimmers, trim_args)
    subprocess.run.assert_any_call(
        ['java', '-jar', jar, 'PE', '-trimlog', 'trim.log', fastq1, fastq2, paired1, unpaired1, paired2, unpaired2,
         'ILLUMINACLIP:TruSeq3-PE-2.fa:2:30:10:2:keepBothReads', 'MINLEN:36'], check=True)


def test_trimmomatic_paired_nojarenv(testdir, mock_testclass):
    sample = 'PORL2A'
    fastq1 = sample + '_1.fastq'
    paired1 = sample + '-paired_1.fastq'
    unpaired1 = sample + '-unpaired_1.fastq'
    fastq2 = sample + '_2.fastq'
    paired2 = sample + '-paired_2.fastq'
    unpaired2 = sample + '-unpaired_2.fastq'
    subprocess.run = MagicMock()
    t.trimmomatic_paired(fastq1, paired1, unpaired1, fastq2, paired2, unpaired2, None, ())
    subprocess.run.assert_any_call(
        ['java', '-jar', 'trimmomatic.jar', 'PE', fastq1, fastq2, paired1, unpaired1, paired2, unpaired2], check=True)


def test_trimmomatic_paired_sbatchmemenv(testdir, mock_testclass):
    jar = 'trimmomatic/trimmomatic.jar'
    os.environ[TRIMMOMATIC_JAR_ENV] = jar
    mem = '48G'
    os.environ[SBATCH_JAVA_MEM_ENV] = mem
    sample = 'PORL2A'
    fastq1 = sample + '_1.fastq'
    paired1 = sample + '-paired_1.fastq'
    unpaired1 = sample + '-unpaired_1.fastq'
    fastq2 = sample + '_2.fastq'
    paired2 = sample + '-paired_2.fastq'
    unpaired2 = sample + '-unpaired_2.fastq'
    subprocess.run = MagicMock()
    t.trimmomatic_paired(fastq1, paired1, unpaired1, fastq2, paired2, unpaired2, None, ())
    subprocess.run.assert_any_call(
        ['java', '-Xmx49152M', '-jar', 'trimmomatic/trimmomatic.jar', 'PE', fastq1, fastq2, paired1, unpaired1, paired2,
         unpaired2], check=True)


def test_sbatch_memory_kilo(mock_testclass):
    assert '2' == t.sbatch_memory('2048K')
    assert '1' == t.sbatch_memory('1100K')
    assert '0' == t.sbatch_memory('512K')


def test_sbatch_memory_meg(mock_testclass):
    assert '2048' == t.sbatch_memory('2048M')
    assert '1100' == t.sbatch_memory('1100M')
    assert '512' == t.sbatch_memory('512M')


def test_sbatch_memory_nounit(mock_testclass):
    assert '2048' == t.sbatch_memory('2048')
    assert '1100' == t.sbatch_memory('1100')
    assert '512' == t.sbatch_memory('512')


def test_sbatch_memory_gig(mock_testclass):
    assert '2048' == t.sbatch_memory('2G')
    assert '1024' == t.sbatch_memory('1G')
    assert '5120' == t.sbatch_memory('5G')


def test_sbatch_memory_tera(mock_testclass):
    assert '2097152' == t.sbatch_memory('2T')
    assert '1048576' == t.sbatch_memory('1T')
    assert '5242880' == t.sbatch_memory('5T')


def test_sbatch_memory_none(mock_testclass):
    assert not t.sbatch_memory(None)
