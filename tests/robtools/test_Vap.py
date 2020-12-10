import logging
import os
from pathlib import Path
import random
from shutil import copyfile
import shutil
import subprocess
from unittest.mock import MagicMock, ANY

import click
from click.testing import CliRunner
from more_itertools.more import side_effect
import pytest

from robtools import Split
from robtools import Vap as v
from robtools.txt import Parser


@pytest.fixture
def mock_testclass():
    vap_samples = v.vap_samples
    vap_sample = v.vap_sample
    create_parameters = v.create_parameters
    parse_genes = v.parse_genes
    parse_heatmap_values = v.parse_heatmap_values
    create_heatmap = v.create_heatmap
    first = Parser.first
    splits = Split.splits
    run = subprocess.run
    rmtree = shutil.rmtree
    yield
    v.vap_samples = vap_samples
    v.vap_sample = vap_sample
    v.create_parameters = create_parameters
    v.parse_genes = parse_genes
    v.parse_heatmap_values = parse_heatmap_values
    v.create_heatmap = create_heatmap
    Parser.first = first
    Split.splits = splits
    subprocess.run = run
    shutil.rmtree = rmtree


def test_vap(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    parameters = Path(__file__).parent.joinpath('parameters.txt')
    v.vap_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(v.vap, ['-s', samples, '-p', parameters])
    assert result.exit_code == 0
    v.vap_samples.assert_called_once_with(samples, parameters, None, None)


def test_vap_parameters(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    parameters = Path(__file__).parent.joinpath('parameters.txt')
    selection = Path(__file__).parent.joinpath('genes.txt')
    index = 1
    v.vap_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(v.vap, ['-s', samples, '-p', parameters, '--selection', selection, '-i', index])
    assert result.exit_code == 0
    v.vap_samples.assert_called_once_with(samples, parameters, selection, index)


def test_vap_samplesnotexists(testdir, mock_testclass):
    samples = 'samples.txt'
    parameters = Path(__file__).parent.joinpath('parameters.txt')
    v.vap_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(v.vap, ['-s', samples, '-p', parameters])
    assert result.exit_code != 0
    v.vap_samples.assert_not_called()


def test_vap_parametersnotexists(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    parameters = 'parameters.txt'
    v.vap_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(v.vap, ['-s', samples, '-p', parameters])
    assert result.exit_code != 0
    v.vap_samples.assert_not_called()


def test_vap_selectionnotexists(testdir, mock_testclass):
    samples = Path(__file__).parent.joinpath('samples.txt')
    parameters = Path(__file__).parent.joinpath('parameters.txt')
    selection = 'genes.txt'
    v.vap_samples = MagicMock()
    runner = CliRunner()
    result = runner.invoke(v.vap, ['-s', samples, '-p', parameters, '--selection', selection])
    assert result.exit_code != 0
    v.vap_samples.assert_not_called()


def test_vap_samples(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    Parser.first = MagicMock(return_value=samples)
    v.vap_sample = MagicMock()
    v.vap_samples(samples_file)
    for sample in samples:
        v.vap_sample.assert_any_call(sample, 'parameters.txt', None)
    Parser.first.assert_called_once_with(samples_file)


def test_vap_samples_parameters(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    parameters = Path(__file__).parent.joinpath('parameters.txt')
    selection = Path(__file__).parent.joinpath('genes.txt')
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    Parser.first = MagicMock(return_value=samples)
    v.vap_sample = MagicMock()
    v.vap_samples(samples_file, parameters, selection)
    for sample in samples:
        v.vap_sample.assert_any_call(sample, parameters, selection)
    Parser.first.assert_called_once_with(samples_file)


def test_vap_samples_second(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    Parser.first = MagicMock(return_value=samples)
    v.vap_sample = MagicMock()
    v.vap_samples(samples_file, index=1)
    v.vap_sample.assert_any_call(samples[1], 'parameters.txt', None)
    Parser.first.assert_called_once_with(samples_file)


def test_vap_samples_second_parameters(testdir, mock_testclass):
    samples_file = Path(__file__).parent.joinpath('samples.txt')
    parameters = Path(__file__).parent.joinpath('parameters.txt')
    selection = Path(__file__).parent.joinpath('genes.txt')
    samples = ['POLR2A', 'ASDURF', 'POLR1C']
    Parser.first = MagicMock(return_value=samples)
    v.vap_sample = MagicMock()
    v.vap_samples(samples_file, parameters, selection, 1)
    v.vap_sample.assert_any_call(samples[1], parameters, selection)
    Parser.first.assert_called_once_with(samples_file)


def test_vap_sample(testdir, mock_testclass):
    sample = 'POLR2A'
    parameters = Path(__file__).parent.joinpath('parameters.txt')
    selection = Path(__file__).parent.joinpath('genes.txt')
    splits = ['POLR2A-100-110', 'POLR2A-120-130']
    genes = ['YDR524W-C', 'YLR355C', 'YLR110C', 'YGR192C', 'YGL008C', 'YKL060C']
    beds = [split + '-cov.bed' for split in splits]
    output = sample + '-vap-output'
    sample_parameters = output + '/parameters.txt'
    splits_values = {}
    for split in splits:
        splits_values[split] = {}
        for gene in genes:
            splits_values[split][gene] = str(random.random())
    merged_heatmap = sample + '-heatmap.txt'
    Split.splits = MagicMock(return_value=splits)
    v.parse_genes = MagicMock(return_value=genes)
    v.create_parameters = MagicMock()
    subprocess.run = MagicMock()
    v.parse_heatmap_values = MagicMock(return_value=splits_values)
    v.create_heatmap = MagicMock()
    shutil.rmtree = MagicMock()
    v.vap_sample(sample, parameters, selection)
    Split.splits.assert_called_once_with(sample)
    v.parse_genes.assert_called_once_with(parameters, selection)
    v.create_parameters.assert_called_once_with(beds, output, selection, parameters, sample_parameters)
    cmd = ['vap']
    if os.name == 'nt':
        cmd = ['vap.exe']
    cmd.extend(['-p', sample_parameters])
    subprocess.run.assert_called_once_with(cmd, check=True)
    v.parse_heatmap_values.assert_called_once_with(splits, output)
    v.create_heatmap.assert_called_once_with(sample, genes, splits, splits_values, merged_heatmap)
    shutil.rmtree.assert_called_once_with(output)


def test_vap_sample_parseheatmaperror(testdir, mock_testclass):
    sample = 'POLR2A'
    parameters = Path(__file__).parent.joinpath('parameters.txt')
    selection = Path(__file__).parent.joinpath('genes.txt')
    splits = ['POLR2A-100-110', 'POLR2A-120-130']
    genes = ['YDR524W-C', 'YLR355C', 'YLR110C', 'YGR192C', 'YGL008C', 'YKL060C']
    beds = [split + '-cov.bed' for split in splits]
    output = sample + '-vap-output'
    sample_parameters = output + '/parameters.txt'
    Split.splits = MagicMock(return_value=splits)
    v.parse_genes = MagicMock(return_value=genes)
    v.create_parameters = MagicMock()
    subprocess.run = MagicMock()
    v.parse_heatmap_values = MagicMock(side_effect=AssertionError)
    v.create_heatmap = MagicMock()
    with pytest.raises(AssertionError):
        v.vap_sample(sample, parameters, selection)


def test_create_parameters(testdir, mock_testclass):
    parameters = Path(__file__).parent.joinpath('parameters.txt')
    beds = ['POLR2A-100-110.bed', 'POLR2A-120-130.bed']
    output_folder = 'output'
    parameters_output = 'params-out.txt'
    v.create_parameters(beds, output_folder, None, parameters, parameters_output)
    with open(parameters, 'r') as expectedfile, open(parameters_output, 'r') as actualfile:
        expected = expectedfile.readline()
        while expected != '':
            if expected.startswith('~~@dataset_path='):
                for bed in beds:
                    assert '~~@dataset_path=R1:=:' + bed + '\n' == actualfile.readline()
            elif expected.startswith('~~@output_directory='):
                assert '~~@output_directory=' + output_folder + '\n' == actualfile.readline()
            elif expected.startswith('~~@prefix_filename='):
                assert '~~@prefix_filename=\n' == actualfile.readline()
            elif expected.startswith('~~@selection_path='):
                assert '~~@selection_path=\n' == actualfile.readline()
            else:
                assert expected == actualfile.readline()
            expected = expectedfile.readline()
        assert actualfile.readline() == ''


def test_create_parameters_selection(testdir, mock_testclass):
    parameters = Path(__file__).parent.joinpath('parameters.txt')
    selection = Path(__file__).parent.joinpath('selection.txt')
    beds = ['POLR2A-100-110.bed', 'POLR2A-120-130.bed']
    output_folder = 'output'
    parameters_output = 'params-out.txt'
    v.create_parameters(beds, output_folder, selection, parameters, parameters_output)
    with open(parameters, 'r') as expectedfile, open(parameters_output, 'r') as actualfile:
        expected = expectedfile.readline()
        while expected != '':
            if expected.startswith('~~@dataset_path='):
                for bed in beds:
                    assert '~~@dataset_path=R1:=:' + bed + '\n' == actualfile.readline()
            elif expected.startswith('~~@output_directory='):
                assert '~~@output_directory=' + output_folder + '\n' == actualfile.readline()
            elif expected.startswith('~~@prefix_filename='):
                assert '~~@prefix_filename=\n' == actualfile.readline()
            elif expected.startswith('~~@selection_path='):
                assert '~~@selection_path=' + str(selection) + '\n' == actualfile.readline()
            else:
                assert expected == actualfile.readline()
            expected = expectedfile.readline()
        assert actualfile.readline() == ''


def test_parse_genes(testdir, mock_testclass):
    parameters = 'parameters.txt'
    copyfile(Path(__file__).parent.joinpath('parameters.txt'), parameters)
    copyfile(Path(__file__).parent.joinpath('genes.txt'), 'genes.txt')
    genes = v.parse_genes(parameters)
    assert genes[0] == 'YDR524W-C'
    assert genes[1] == 'YLR355C'
    assert genes[2] == 'YLR110C'
    assert genes[3] == 'YGR192C'
    assert genes[4] == 'YGL008C'
    assert genes[5] == 'YKL060C'


def test_parse_genes_selection(testdir, mock_testclass):
    parameters = 'parameters_selection.txt'
    copyfile(Path(__file__).parent.joinpath('parameters_selection.txt'), parameters)
    copyfile(Path(__file__).parent.joinpath('genes.txt'), 'genes.txt')
    selection = Path(__file__).parent.joinpath('selection.txt')
    genes = v.parse_genes(parameters, selection)
    assert genes[0] == 'YLR110C'
    assert genes[1] == 'YGL008C'


def test_parse_heatmap_values(testdir, mock_testclass):
    sample_splits = ['POLR2A-100-110', 'POLR2A-120-130']
    output_folder = str(testdir)
    copyfile(Path(__file__).parent.joinpath('ind_data_POLR2A-100-110.txt'), 'ind_data_POLR2A-100-110.txt')
    copyfile(Path(__file__).parent.joinpath('ind_data_POLR2A-120-130.txt'), 'ind_data_POLR2A-120-130.txt')
    heatmap = v.parse_heatmap_values(sample_splits, output_folder)
    for split in sample_splits:
        assert split in heatmap
    assert 'YCR088W' in heatmap['POLR2A-100-110']
    assert heatmap['POLR2A-100-110']['YCR088W'] == '1.2'
    assert 'YMR282C' in heatmap['POLR2A-100-110']
    assert heatmap['POLR2A-100-110']['YMR282C'] == '2.408'
    assert 'YOR374W' in heatmap['POLR2A-100-110']
    assert heatmap['POLR2A-100-110']['YOR374W'] == '0.34'
    assert 'YPR185W' in heatmap['POLR2A-100-110']
    assert heatmap['POLR2A-100-110']['YPR185W'] == '0.978'
    assert 'YPL259C' in heatmap['POLR2A-100-110']
    assert heatmap['POLR2A-100-110']['YPL259C'] == '1.5883'
    assert 'YER107C' in heatmap['POLR2A-120-130']
    assert heatmap['POLR2A-120-130']['YER107C'] == '1.32'
    assert 'YEL056W' in heatmap['POLR2A-120-130']
    assert heatmap['POLR2A-120-130']['YEL056W'] == '1.9516'
    assert 'YNL037C' in heatmap['POLR2A-120-130']
    assert heatmap['POLR2A-120-130']['YNL037C'] == '0'
    assert 'YDR017C' in heatmap['POLR2A-120-130']
    assert heatmap['POLR2A-120-130']['YDR017C'] == '0.832'
    assert 'YKL186C' in heatmap['POLR2A-120-130']
    assert heatmap['POLR2A-120-130']['YKL186C'] == '0.224'


def test_parse_heatmap_values_noheatmapfiles(testdir, mock_testclass):
    sample_splits = ['POLR2A-100-110', 'POLR2A-120-130']
    output_folder = str(os.curdir)
    with pytest.raises(AssertionError):
        v.parse_heatmap_values(sample_splits, output_folder)


def test_create_heatmap(testdir, mock_testclass):
    sample = 'POLR2A'
    genes = ['YDR524W-C', 'YLR355C', 'YLR110C', 'YGR192C', 'YGL008C', 'YKL060C']
    splits = ['POLR2A-100-110', 'POLR2A-120-130']
    splits_values = {}
    for split in splits:
        splits_values[split] = {}
        for gene in genes:
            splits_values[split][gene] = str(random.random())
    output = 'out.txt'
    v.create_heatmap(sample, genes, splits, splits_values, output)
    with open(output, 'r') as infile:
        assert infile.readline() == 'UNIQID\tName\t100-110\t120-130\n'
        assert infile.readline() == 'EWEIGHT\t\t1\t1\n'
        assert infile.readline() == 'YDR524W-C\tYDR524W-C\t' + splits_values['POLR2A-100-110']['YDR524W-C'] + '\t' + splits_values['POLR2A-120-130']['YDR524W-C'] + '\n'
        assert infile.readline() == 'YLR355C\tYLR355C\t' + splits_values['POLR2A-100-110']['YLR355C'] + '\t' + splits_values['POLR2A-120-130']['YLR355C'] + '\n'
        assert infile.readline() == 'YLR110C\tYLR110C\t' + splits_values['POLR2A-100-110']['YLR110C'] + '\t' + splits_values['POLR2A-120-130']['YLR110C'] + '\n'
        assert infile.readline() == 'YGR192C\tYGR192C\t' + splits_values['POLR2A-100-110']['YGR192C'] + '\t' + splits_values['POLR2A-120-130']['YGR192C'] + '\n'
        assert infile.readline() == 'YGL008C\tYGL008C\t' + splits_values['POLR2A-100-110']['YGL008C'] + '\t' + splits_values['POLR2A-120-130']['YGL008C'] + '\n'
        assert infile.readline() == 'YKL060C\tYKL060C\t' + splits_values['POLR2A-100-110']['YKL060C'] + '\t' + splits_values['POLR2A-120-130']['YKL060C'] + '\n'
        assert infile.readline() == ''
