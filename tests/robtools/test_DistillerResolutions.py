from pathlib import Path

from click.testing import CliRunner

from robtools import DistillerResolutions as dr


def test_distillerresolutions(testdir):
    project = Path(__file__).parent.joinpath('project.yml')
    runner = CliRunner()
    result = runner.invoke(dr.distillerresolutions, ['--project', project])
    assert result.exit_code == 0
    assert result.stdout == '10000\n5000\n2000\n1000\n500\n200\n100\n50\n20\n10\n'


def test_distillerresolutions_parameters(testdir):
    project = Path(__file__).parent.joinpath('project_lessresolutions.yml')
    runner = CliRunner()
    result = runner.invoke(dr.distillerresolutions, ['--project', project])
    assert result.exit_code == 0
    assert result.stdout == '1000000\n500000\n250000\n100000\n50000\n25000\n10000\n'


def test_distillerresolutions_error(testdir):
    project = Path(__file__).parent.joinpath('project_error.yml')
    runner = CliRunner()
    result = runner.invoke(dr.distillerresolutions, ['--project', project])
    assert result.exit_code != 0
