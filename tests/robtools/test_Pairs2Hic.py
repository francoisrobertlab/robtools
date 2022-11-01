import gzip
import os
import shutil
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, ANY

import pytest
from click.testing import CliRunner
from yaml.scanner import ScannerError

from robtools import Pairs2Hic


@pytest.fixture
def mock_testclass():
    pairs2hic_ = Pairs2Hic.pairs2hic_
    pairs_to_hic = Pairs2Hic.pairs_to_hic
    pairs_to_medium = Pairs2Hic.pairs_to_medium
    resolve = Pairs2Hic.resolve
    merge_pairs = Pairs2Hic.merge_pairs
    run = subprocess.run
    os_remove = os.remove
    yield
    Pairs2Hic.pairs2hic_ = pairs2hic_
    Pairs2Hic.pairs_to_hic = pairs_to_hic
    subprocess.run = run
    Pairs2Hic.pairs_to_medium = pairs_to_medium
    Pairs2Hic.resolve = resolve
    Pairs2Hic.merge_pairs = merge_pairs
    os.remove = os_remove


def copy_sort(*args, **kwargs):
    to_sort = args[0][len(args[0]) - 1]
    output = args[0][args[0].index('-o') + 1]
    with open(to_sort) as to_sort_in, open(output, 'w') as output_out:
        lines = to_sort_in.readlines()
        for i in range(0, len(lines)):
            output_out.write(lines[len(lines) - i - 1])


def test_pairs2hic(testdir, mock_testclass):
    project = Path(__file__).parent.joinpath("project.yml")
    juicer = "juicer_tools.jar"
    Path(juicer).touch()
    Pairs2Hic.pairs2hic_ = MagicMock()
    runner = CliRunner()
    result = runner.invoke(Pairs2Hic.pairs2hic, ["--project", project])
    print(result.output)
    assert result.exit_code == 0
    Pairs2Hic.pairs2hic_.assert_called_once_with(project, "juicer_tools.jar", None, None, ())


def test_pairs2hic_parameters(testdir, mock_testclass):
    project = Path(__file__).parent.joinpath("project.yml")
    juicer = "juicer_tools_2.16.0.jar"
    Path(juicer).touch()
    output_suffix = "-mapq30"
    output_folder = "output-folder"
    os.mkdir(output_folder)
    Pairs2Hic.pairs2hic_ = MagicMock()
    runner = CliRunner()
    result = runner.invoke(Pairs2Hic.pairs2hic,
                           ["--project", project, "--juicer", juicer, "--output-suffix", output_suffix,
                            "--output-folder", output_folder, "-m", "30"])
    print(result.output)
    assert result.exit_code == 0
    Pairs2Hic.pairs2hic_.assert_called_once_with(project, juicer, output_suffix, output_folder, ("-m", "30"))


def test_pairs2hic_projectnotexists(testdir, mock_testclass):
    project = "project.yml"
    juicer = "juicer_tools.jar"
    Path(juicer).touch()
    Pairs2Hic.pairs2hic_ = MagicMock()
    runner = CliRunner()
    result = runner.invoke(Pairs2Hic.pairs2hic, ["--project", project])
    print(result.output)
    assert result.exit_code != 0
    Pairs2Hic.pairs2hic_.assert_not_called()


def test_pairs2hic_juicernotexists(testdir, mock_testclass):
    project = Path(__file__).parent.joinpath("project.yml")
    Pairs2Hic.pairs2hic_ = MagicMock()
    runner = CliRunner()
    result = runner.invoke(Pairs2Hic.pairs2hic, ["--project", project])
    print(result.output)
    assert result.exit_code != 0
    Pairs2Hic.pairs2hic_.assert_not_called()


def test_pairs2hic_outputfoldernotexists(testdir, mock_testclass):
    project = Path(__file__).parent.joinpath("project.yml")
    juicer = "juicer_tools.jar"
    Path(juicer).touch()
    output_folder = "output-folder"
    Pairs2Hic.pairs2hic_ = MagicMock()
    runner = CliRunner()
    result = runner.invoke(Pairs2Hic.pairs2hic, ["--project", project, "--output-folder", output_folder])
    print(result.output)
    assert result.exit_code != 0
    Pairs2Hic.pairs2hic_.assert_not_called()


def test_pairs2hic_(testdir, mock_testclass):
    project = "project.yml"
    shutil.copy(Path(__file__).parent.joinpath("project.yml"), project)
    juicer = "juicer_tools.jar"
    Path(juicer).touch()
    pairs1 = "CJ1_MicroC_WT.pairs.gz"
    Path(pairs1).touch()
    hic1 = "CJ1_MicroC_WT.hic"
    pairs2 = "CJ2_MicroC_FACT.pairs.gz"
    Path(pairs2).touch()
    hic2 = "CJ2_MicroC_FACT.hic"
    hic3 = "all_libraries.hic"
    resolutions = [10000, 5000, 2000, 1000, 500, 200, 100, 50, 20, 10]
    chromosome_sizes = "sacCer3.chrom.sizes"
    Path(chromosome_sizes).touch()
    output_folder = "."
    Pairs2Hic.pairs_to_hic = MagicMock()
    Pairs2Hic.resolve = MagicMock(side_effect=[chromosome_sizes, pairs1, pairs2, pairs1, pairs2])
    Pairs2Hic.merge_pairs = MagicMock()
    Pairs2Hic.pairs2hic_(project, juicer)
    Pairs2Hic.resolve.assert_any_call(chromosome_sizes, [''])
    Pairs2Hic.resolve.assert_any_call("CJ1_MicroC_WT.*.pairs.gz", [''])
    Pairs2Hic.resolve.assert_any_call("CJ2_MicroC_FACT.*.pairs.gz", [''])
    Pairs2Hic.merge_pairs.assert_called_once_with([pairs1, pairs2], ANY)
    Pairs2Hic.pairs_to_hic.assert_any_call(pairs1, os.path.join(output_folder, hic1), resolutions, chromosome_sizes,
                                           juicer, ())
    Pairs2Hic.pairs_to_hic.assert_any_call(pairs2, os.path.join(output_folder, hic2), resolutions, chromosome_sizes,
                                           juicer, ())
    Pairs2Hic.pairs_to_hic.assert_any_call(ANY, os.path.join(output_folder, hic3), resolutions, chromosome_sizes,
                                           juicer, ())
    assert Pairs2Hic.pairs_to_hic.call_args_list[2].args[0] == Pairs2Hic.merge_pairs.call_args_list[0].args[1]


def test_pairs2hic_projectinsiblingdir(testdir, mock_testclass):
    directory = "new_current_dir"
    os.mkdir(directory)
    os.chdir(directory)
    project = "../project/project.yml"
    os.mkdir("../project")
    shutil.copy(Path(__file__).parent.joinpath("project.yml"), project)
    juicer = "../project/juicer_tools.jar"
    Path(juicer).touch()
    pairs1 = "CJ1_MicroC_WT.pairs.gz"
    Path(pairs1).touch()
    hic1 = "CJ1_MicroC_WT.hic"
    pairs2 = "CJ2_MicroC_FACT.pairs.gz"
    Path(pairs2).touch()
    hic2 = "CJ2_MicroC_FACT.hic"
    hic3 = "all_libraries.hic"
    resolutions = [10000, 5000, 2000, 1000, 500, 200, 100, 50, 20, 10]
    chromosome_sizes = "sacCer3.chrom.sizes"
    Path(chromosome_sizes).touch()
    output_folder = "."
    Pairs2Hic.pairs_to_hic = MagicMock()
    Pairs2Hic.resolve = MagicMock(side_effect=[chromosome_sizes, pairs1, pairs2, pairs1, pairs2])
    Pairs2Hic.merge_pairs = MagicMock()
    Pairs2Hic.pairs2hic_(project, juicer)
    Pairs2Hic.resolve.assert_any_call(chromosome_sizes, ['../project', ''])
    Pairs2Hic.resolve.assert_any_call("CJ1_MicroC_WT.*.pairs.gz", ['../project', ''])
    Pairs2Hic.resolve.assert_any_call("CJ2_MicroC_FACT.*.pairs.gz", ['../project', ''])
    Pairs2Hic.merge_pairs.assert_called_once_with([pairs1, pairs2], ANY)
    Pairs2Hic.pairs_to_hic.assert_any_call(pairs1, os.path.join(output_folder, hic1), resolutions, chromosome_sizes,
                                           juicer, ())
    Pairs2Hic.pairs_to_hic.assert_any_call(pairs2, os.path.join(output_folder, hic2), resolutions, chromosome_sizes,
                                           juicer, ())
    Pairs2Hic.pairs_to_hic.assert_any_call(ANY, os.path.join(output_folder, hic3), resolutions, chromosome_sizes,
                                           juicer, ())
    assert Pairs2Hic.pairs_to_hic.call_args_list[2].args[0] == Pairs2Hic.merge_pairs.call_args_list[0].args[1]


def test_pairs2hic_relativegenome(testdir, mock_testclass):
    directory = "new_current_dir"
    os.mkdir(directory)
    os.chdir(directory)
    project = "../project/project.yml"
    os.mkdir("../project")
    shutil.copy(Path(__file__).parent.joinpath("project_relativegenome.yml"), project)
    juicer = "../project/juicer_tools.jar"
    Path(juicer).touch()
    pairs1 = "CJ1_MicroC_WT.pairs.gz"
    Path(pairs1).touch()
    hic1 = "CJ1_MicroC_WT.hic"
    pairs2 = "CJ2_MicroC_FACT.pairs.gz"
    Path(pairs2).touch()
    hic2 = "CJ2_MicroC_FACT.hic"
    hic3 = "all_libraries.hic"
    resolutions = [10000, 5000, 2000, 1000, 500, 200, 100, 50, 20, 10]
    chromosome_sizes = "sacCer3.chrom.sizes"
    os.mkdir("../project/sacCer3")
    Path("../project/sacCer3/" + chromosome_sizes).touch()
    output_folder = "."
    Pairs2Hic.pairs_to_hic = MagicMock()
    Pairs2Hic.resolve = MagicMock(side_effect=[chromosome_sizes, pairs1, pairs2, pairs1, pairs2])
    Pairs2Hic.merge_pairs = MagicMock()
    Pairs2Hic.pairs2hic_(project, juicer)
    Pairs2Hic.resolve.assert_any_call(chromosome_sizes, ['../project/sacCer3', '../project', ''])
    Pairs2Hic.resolve.assert_any_call("CJ1_MicroC_WT.*.pairs.gz", ['../project', ''])
    Pairs2Hic.resolve.assert_any_call("CJ2_MicroC_FACT.*.pairs.gz", ['../project', ''])
    Pairs2Hic.merge_pairs.assert_called_once_with([pairs1, pairs2], ANY)
    Pairs2Hic.pairs_to_hic.assert_any_call(pairs1, os.path.join(output_folder, hic1), resolutions, chromosome_sizes,
                                           juicer, ())
    Pairs2Hic.pairs_to_hic.assert_any_call(pairs2, os.path.join(output_folder, hic2), resolutions, chromosome_sizes,
                                           juicer, ())
    Pairs2Hic.pairs_to_hic.assert_any_call(ANY, os.path.join(output_folder, hic3), resolutions, chromosome_sizes,
                                           juicer, ())
    assert Pairs2Hic.pairs_to_hic.call_args_list[2].args[0] == Pairs2Hic.merge_pairs.call_args_list[0].args[1]


def test_pairs2hic__parameters(testdir, mock_testclass):
    project_folder = Path(__file__).parent
    project = os.path.join(project_folder, "project.yml")
    juicer = "juicer_tools.jar"
    Path(juicer).touch()
    output_suffix = "-mapq30"
    pairs1 = "CJ1_MicroC_WT.pairs.gz"
    Path(pairs1).touch()
    hic1 = "CJ1_MicroC_WT" + output_suffix + ".hic"
    pairs2 = "CJ2_MicroC_FACT.pairs.gz"
    Path(pairs2).touch()
    hic2 = "CJ2_MicroC_FACT" + output_suffix + ".hic"
    hic3 = "all_libraries" + output_suffix + ".hic"
    resolutions = [10000, 5000, 2000, 1000, 500, 200, 100, 50, 20, 10]
    chromosome_sizes = "sacCer3.chrom.sizes"
    Path(chromosome_sizes).touch()
    output_folder = "output-folder"
    os.mkdir(output_folder)
    Pairs2Hic.pairs_to_hic = MagicMock()
    Pairs2Hic.resolve = MagicMock(side_effect=[chromosome_sizes, pairs1, pairs2, pairs1, pairs2])
    Pairs2Hic.merge_pairs = MagicMock()
    Pairs2Hic.pairs2hic_(project, juicer, output_suffix, output_folder, ("-m", "30"))
    Pairs2Hic.resolve.assert_any_call(chromosome_sizes, [str(project_folder), ''])
    Pairs2Hic.resolve.assert_any_call("CJ1_MicroC_WT.*.pairs.gz", [str(project_folder), ''])
    Pairs2Hic.resolve.assert_any_call("CJ2_MicroC_FACT.*.pairs.gz", [str(project_folder), ''])
    Pairs2Hic.merge_pairs.assert_called_once_with([pairs1, pairs2], ANY)
    Pairs2Hic.pairs_to_hic.assert_any_call(pairs1, os.path.join(output_folder, hic1), resolutions, chromosome_sizes,
                                           juicer, ("-m", "30"))
    Pairs2Hic.pairs_to_hic.assert_any_call(pairs2, os.path.join(output_folder, hic2), resolutions, chromosome_sizes,
                                           juicer, ("-m", "30"))
    Pairs2Hic.pairs_to_hic.assert_any_call(ANY, os.path.join(output_folder, hic3), resolutions, chromosome_sizes,
                                           juicer, ("-m", "30"))
    assert Pairs2Hic.pairs_to_hic.call_args_list[2].args[0] == Pairs2Hic.merge_pairs.call_args_list[0].args[1]


def test_pairs2hic__projecterror(testdir, mock_testclass):
    project = "project.yml"
    shutil.copy(Path(__file__).parent.joinpath("project_error.yml"), project)
    juicer = "juicer_tools.jar"
    Path(juicer).touch()
    pairs1 = "CJ1_MicroC_WT.pairs.gz"
    Path(pairs1).touch()
    pairs2 = "CJ2_MicroC_FACT.pairs.gz"
    Path(pairs2).touch()
    chromosome_sizes = "sacCer3.chrom.sizes"
    Path(chromosome_sizes).touch()
    Pairs2Hic.pairs_to_hic = MagicMock()
    Pairs2Hic.resolve = MagicMock(side_effect=[chromosome_sizes, pairs1, pairs2, pairs1, pairs2])
    Pairs2Hic.merge_pairs = MagicMock()
    with pytest.raises(ScannerError):
        Pairs2Hic.pairs2hic_(project, juicer)


def test_pairs2hic__chromosomesizesnotexists(testdir, mock_testclass):
    project = "project.yml"
    shutil.copy(Path(__file__).parent.joinpath("project.yml"), project)
    juicer = "juicer_tools.jar"
    Path(juicer).touch()
    pairs1 = "CJ1_MicroC_WT.pairs.gz"
    Path(pairs1).touch()
    pairs2 = "CJ2_MicroC_FACT.pairs.gz"
    Path(pairs2).touch()
    chromosome_sizes = "sacCer3.chrom.sizes"
    Path(chromosome_sizes).touch()
    Pairs2Hic.pairs_to_hic = MagicMock()
    Pairs2Hic.resolve = MagicMock(side_effect=[None, pairs1, pairs2, pairs1, pairs2])
    Pairs2Hic.merge_pairs = MagicMock()
    with pytest.raises(SystemExit) as sys_exit:
        Pairs2Hic.pairs2hic_(project, juicer)
    assert sys_exit.type == SystemExit
    assert sys_exit.value.code == 1


def test_pairs2hic__pairs2notexists(testdir, mock_testclass):
    project = "project.yml"
    shutil.copy(Path(__file__).parent.joinpath("project.yml"), project)
    juicer = "juicer_tools.jar"
    Path(juicer).touch()
    pairs1 = "CJ1_MicroC_WT.pairs.gz"
    Path(pairs1).touch()
    hic1 = "CJ1_MicroC_WT.hic"
    pairs2 = "CJ2_MicroC_FACT.pairs.gz"
    Path(pairs2).touch()
    hic2 = "CJ2_MicroC_FACT.hic"
    resolutions = [10000, 5000, 2000, 1000, 500, 200, 100, 50, 20, 10]
    chromosome_sizes = "sacCer3.chrom.sizes"
    Path(chromosome_sizes).touch()
    output_folder = "."
    Pairs2Hic.pairs_to_hic = MagicMock()
    Pairs2Hic.resolve = MagicMock(side_effect=[chromosome_sizes, pairs1, None, pairs1, None])
    Pairs2Hic.merge_pairs = MagicMock()
    Pairs2Hic.pairs2hic_(project, juicer)
    Pairs2Hic.resolve.assert_any_call(chromosome_sizes, [''])
    Pairs2Hic.resolve.assert_any_call("CJ1_MicroC_WT.*.pairs.gz", [''])
    Pairs2Hic.resolve.assert_any_call("CJ2_MicroC_FACT.*.pairs.gz", [''])
    Pairs2Hic.pairs_to_hic.assert_called_once_with(pairs1, os.path.join(output_folder, hic1), resolutions,
                                                   chromosome_sizes, juicer, ())


def test_pairs_to_hic(testdir, mock_testclass):
    juicer = "juicer_tools.jar"
    Path(juicer).touch()
    pairs = "CJ1_MicroC_WT.pairs.gz"
    Path(pairs).touch()
    hic = "CJ1_MicroC_WT.hic"
    resolutions = [10000, 5000, 2000, 1000, 500, 200, 100, 50, 20, 10]
    chromosome_sizes = "sacCer3.chrom.sizes"
    Path(chromosome_sizes).touch()
    Pairs2Hic.pairs_to_medium = MagicMock()
    subprocess.run = MagicMock()
    Pairs2Hic.pairs_to_hic(pairs, hic, resolutions, chromosome_sizes)
    Pairs2Hic.pairs_to_medium.assert_called_once_with(pairs, ANY)
    subprocess.run.assert_called_once_with(
        ["java", "-jar", juicer, "pre", "-r", ','.join([str(resolution) for resolution in resolutions]), ANY, hic,
         chromosome_sizes], check=True)
    assert subprocess.run.call_args_list[0].args[0][6] == Pairs2Hic.pairs_to_medium.call_args_list[0].args[1]


def test_pairs_to_hic_parameters(testdir, mock_testclass):
    juicer = "juicer_tools_2.16.0.jar"
    Path(juicer).touch()
    juicer_args = ("-m", "30")
    pairs = "CJ1_MicroC_WT.pairs.gz"
    Path(pairs).touch()
    hic = "CJ1_MicroC_WT.hic"
    resolutions = [10000, 5000, 2000, 1000, 500, 200, 100, 50, 20, 10]
    chromosome_sizes = "sacCer3.chrom.sizes"
    Path(chromosome_sizes).touch()
    Pairs2Hic.pairs_to_medium = MagicMock()
    subprocess.run = MagicMock()
    Pairs2Hic.pairs_to_hic(pairs, hic, resolutions, chromosome_sizes, juicer, juicer_args)
    Pairs2Hic.pairs_to_medium.assert_called_once_with(pairs, ANY)
    subprocess.run.assert_called_once_with(
        ["java", "-jar", juicer, "pre", "-m", "30", "-r", ','.join([str(resolution) for resolution in resolutions]),
         ANY, hic, chromosome_sizes], check=True)
    assert subprocess.run.call_args_list[0].args[0][8] == Pairs2Hic.pairs_to_medium.call_args_list[0].args[1]


def test_pairs_to_medium(testdir, mock_testclass):
    pairs = "CJ1_MicroC_WT.pairs.gz"
    with open(Path(__file__).parent.joinpath("CJ1_MicroC_WT.pairs")) as pairs_in, gzip.open(pairs, 'wt') as pairs_out:
        for line in pairs_in:
            pairs_out.write(line)
    medium = "CJ1_MicroC_WT.tsv"
    Pairs2Hic.pairs_to_medium(pairs, medium)
    with open(medium) as medium_in:
        medium_lines = medium_in.readlines()
    assert medium_lines[0] == ".\t0\tchrI\t1\t0\t1\tchrI\t62\t1\t41\t41\n"
    assert medium_lines[1] == ".\t0\tchrI\t1\t0\t1\tchrI\t116\t1\t5\t57\n"
    assert medium_lines[2] == ".\t0\tchrI\t1\t0\t1\tchrI\t196\t1\t32\t60\n"
    assert medium_lines[3] == ".\t0\tchrI\t1\t0\t1\tchrI\t255\t1\t5\t60\n"
    assert medium_lines[4] == ".\t0\tchrI\t1\t0\t0\tchrI\t460\t1\t29\t60\n"
    assert medium_lines[5] == ".\t0\tchrI\t1\t0\t1\tchrI\t16623\t1\t60\t31\n"
    assert medium_lines[6] == ".\t0\tchrXVI\t943105\t0\t1\tchrXVI\t943348\t1\t23\t1\n"
    assert medium_lines[7] == ".\t0\tchrXVI\t943144\t0\t1\tchrXVI\t943243\t1\t6\t6\n"
    assert medium_lines[8] == ".\t1\tchrXVI\t943172\t0\t0\tchrXVI\t943251\t1\t8\t1\n"
    assert medium_lines[9] == ".\t0\tchrXVI\t943187\t0\t1\tchrXVI\t946327\t1\t5\t10\n"
    assert medium_lines[10] == ".\t0\tchrXVI\t946231\t0\t1\tchrXVI\t946324\t1\t10\t9\n"


def test_resolve(testdir, mock_testclass):
    pairs = "CJ1_MicroC_WT.nodups.pairs.gz"
    pattern = "CJ1_MicroC_WT.*.pairs.gz"
    Path(pairs).touch()
    actual = Pairs2Hic.resolve(pattern, [''])
    assert actual == pairs


def test_resolve_firstfile(testdir, mock_testclass):
    pairs1 = "CJ1_MicroC_WT.nodups.pairs.gz"
    Path(pairs1).touch()
    pairs2 = "CJ1_MicroC_WT.withdups.pairs.gz"
    Path(pairs2).touch()
    Path("CJ2_MicroC_FACT.nodups.pairs.gz").touch()
    pattern = "CJ1_MicroC_WT.*.pairs.gz"
    actual = Pairs2Hic.resolve(pattern, [''])
    assert actual == pairs1 or actual == pairs2  # System dependent


def test_resolve_folder(testdir, mock_testclass):
    pairs = "CJ1_MicroC_WT.nodups.pairs.gz"
    pattern = "CJ1_MicroC_WT.*.pairs.gz"
    folder = "test"
    os.mkdir(folder)
    expected = os.path.join(folder, pairs)
    Path(expected).touch()
    Path(os.path.join(folder, "CJ2_MicroC_FACT.nodups.pairs.gz")).touch()
    actual = Pairs2Hic.resolve(pattern, [folder])
    assert actual == expected


def test_resolve_firstfolder(testdir, mock_testclass):
    pairs = "CJ1_MicroC_WT.nodups.pairs.gz"
    pattern = "CJ1_MicroC_WT.*.pairs.gz"
    folder1 = "first"
    os.mkdir(folder1)
    folder2 = "second"
    os.mkdir(folder2)
    expected = os.path.join(folder1, pairs)
    Path(expected).touch()
    Path(os.path.join(folder1, "CJ2_MicroC_FACT.nodups.pairs.gz")).touch()
    actual = Pairs2Hic.resolve(pattern, [folder1, folder2])
    assert actual == expected


def test_resolve_secondfolder(testdir, mock_testclass):
    pairs = "CJ1_MicroC_WT.nodups.pairs.gz"
    pattern = "CJ1_MicroC_WT.*.pairs.gz"
    folder1 = "first"
    os.mkdir(folder1)
    folder2 = "second"
    os.mkdir(folder2)
    expected = os.path.join(folder2, pairs)
    Path(expected).touch()
    Path(os.path.join(folder2, "CJ2_MicroC_FACT.nodups.pairs.gz")).touch()
    actual = Pairs2Hic.resolve(pattern, [folder1, folder2])
    assert actual == expected


def test_resolve_priority(testdir, mock_testclass):
    pairs = "CJ1_MicroC_WT.nodups.pairs.gz"
    pattern = "CJ1_MicroC_WT.*.pairs.gz"
    folder1 = "first"
    os.mkdir(folder1)
    folder2 = "second"
    os.mkdir(folder2)
    expected = os.path.join(folder1, pairs)
    Path(expected).touch()
    Path(os.path.join(folder2, pairs)).touch()
    Path(os.path.join(folder1, "CJ2_MicroC_FACT.nodups.pairs.gz")).touch()
    Path(os.path.join(folder2, "CJ2_MicroC_FACT.nodups.pairs.gz")).touch()
    actual = Pairs2Hic.resolve(pattern, [folder1, folder2])
    assert actual == expected


def test_merge_pairs(testdir, mock_testclass):
    pairs1 = "CJ1_MicroC_WT.pairs.gz"
    pairs2 = "CJ2_MicroC_FACT.pairs.gz"
    with open(Path(__file__).parent.joinpath("CJ1_MicroC_WT.pairs")) as pairs_in, gzip.open(pairs1, 'wt') as pairs1_out:
        for line in pairs_in:
            pairs1_out.write(line)
    with open(Path(__file__).parent.joinpath("CJ2_MicroC_FACT.pairs")) as pairs_in, gzip.open(pairs2,
                                                                                              'wt') as pairs2_out:
        for line in pairs_in:
            pairs2_out.write(line)
    output = "CJ1_MicroC_WT.tsv"
    subprocess.run = MagicMock(side_effect=copy_sort)
    os.remove = MagicMock()
    Pairs2Hic.merge_pairs([pairs1, pairs2], output)
    subprocess.run.assert_called_once_with(
        ["sort", "-k", "2,2", "-k", "4,4", "-k", "3,3n", "-k", "5,5n", "-o", ANY, ANY], check=True)
    merged_pairs = subprocess.run.call_args_list[0].args[0][len(subprocess.run.call_args_list[0].args[0]) - 1]
    with open(merged_pairs) as merged_pairs_in:
        merged_pairs_lines = merged_pairs_in.readlines()
    with gzip.open(output, 'rt') as output_in:
        output_lines = output_in.readlines()
    assert merged_pairs_lines[0] == ".\tchrI\t1\tchrI\t62\t+\t-\tUU\t41\t41\n"
    assert merged_pairs_lines[1] == ".\tchrI\t1\tchrI\t116\t+\t-\tUU\t5\t57\n"
    assert merged_pairs_lines[2] == ".\tchrI\t1\tchrI\t196\t+\t-\tUU\t32\t60\n"
    assert merged_pairs_lines[3] == ".\tchrI\t1\tchrI\t255\t+\t-\tRU\t5\t60\n"
    assert merged_pairs_lines[4] == ".\tchrI\t1\tchrI\t460\t+\t+\tUU\t29\t60\n"
    assert merged_pairs_lines[5] == ".\tchrI\t1\tchrI\t16623\t+\t-\tRU\t60\t31\n"
    assert merged_pairs_lines[6] == ".\tchrXVI\t943105\tchrXVI\t943348\t+\t-\tUU\t23\t1\n"
    assert merged_pairs_lines[7] == ".\tchrXVI\t943144\tchrXVI\t943243\t+\t-\tUU\t6\t6\n"
    assert merged_pairs_lines[8] == ".\tchrXVI\t943172\tchrXVI\t943251\t-\t+\tUU\t8\t1\n"
    assert merged_pairs_lines[9] == ".\tchrXVI\t943187\tchrXVI\t946327\t+\t-\tUU\t5\t10\n"
    assert merged_pairs_lines[10] == ".\tchrXVI\t946231\tchrXVI\t946324\t+\t-\tUU\t10\t9\n"
    assert merged_pairs_lines[11] == ".\tchrI\t1\tchrI\t56\t+\t-\tUU\t27\t27\n"
    assert merged_pairs_lines[12] == ".\tchrI\t1\tchrI\t58\t+\t-\tUU\t30\t30\n"
    assert merged_pairs_lines[13] == ".\tchrI\t1\tchrI\t62\t+\t-\tUU\t24\t41\n"
    assert merged_pairs_lines[14] == ".\tchrI\t1\tchrI\t72\t+\t-\tUU\t42\t60\n"
    assert merged_pairs_lines[15] == ".\tchrI\t1\tchrI\t77\t+\t-\tUU\t11\t60\n"
    assert merged_pairs_lines[16] == ".\tchrI\t1\tchrI\t128\t+\t-\tUU\t42\t60\n"
    assert merged_pairs_lines[17] == ".\tchrXVI\t942874\tchrXVI\t943296\t-\t-\tUU\t60\t4\n"
    assert merged_pairs_lines[18] == ".\tchrXVI\t943115\tchrXVI\t943206\t+\t-\tUU\t7\t10\n"
    assert merged_pairs_lines[19] == ".\tchrXVI\t943129\tchrXVI\t943200\t+\t-\tUU\t8\t9\n"
    assert merged_pairs_lines[20] == ".\tchrXVI\t943186\tchrXVI\t943282\t+\t-\tUU\t5\t5\n"
    assert merged_pairs_lines[21] == ".\tchrXVI\t946209\tchrXVI\t946297\t+\t-\tUU\t10\t10\n"
    assert len(output_lines) == len(merged_pairs_lines)
    for i in range(0, len(output_lines)):
        assert output_lines[i] == merged_pairs_lines[len(merged_pairs_lines) - i - 1]
