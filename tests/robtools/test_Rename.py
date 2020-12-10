import logging
import os
from pathlib import Path
import pytest
from shutil import copyfile
import subprocess
from unittest.mock import MagicMock, ANY

import click
from click.testing import CliRunner
from robtools import Rename as rn


@pytest.fixture
def mock_testclass():
    rename = rn.rename
    rename_in_md5 = rn.rename_in_md5
    yield 
    rn.rename = rename
    rn.rename_in_md5 = rename_in_md5
    
    
def test_rename(testdir, mock_testclass):
    src_names = Path(__file__).parent.joinpath('names.txt')
    runner = CliRunner()
    with runner.isolated_filesystem():
        names = 'names.txt'
        copyfile(src_names, names)
        Path('test.txt').touch()
        Path('prefix-test.txt').touch()
        Path('prefix-test.txt.gz').touch()
        with open('prefix-test.txt.gz.md5', 'w') as outfile:
            outfile.write('a5b04eadcc374613df01fdeb9a426cfa\tprefix-test.txt.gz\n')
        Path('def.txt').touch()
        Path('prefix-def.txt').touch()
        Path('prefix-def.txt.gz').touch()
        with open('prefix-def.txt.gz.md5', 'w') as outfile:
            outfile.write('ea21f0800b4fec21e86cde364080a198\tprefix-def.txt.gz\n')
        result = runner.invoke(rn.rename, ['--names', names])
        print (result.output)
        assert result.exit_code == 0
        assert not os.path.exists('test.txt')
        assert not os.path.exists('prefix-test.txt')
        assert not os.path.exists('prefix-test.txt.gz')
        assert not os.path.exists('prefix-test.txt.gz.md5')
        assert os.path.exists('abc.txt')
        assert os.path.exists('prefix-abc.txt')
        assert os.path.exists('prefix-abc.txt.gz')
        assert os.path.exists('prefix-abc.txt.gz.md5')
        with open('prefix-abc.txt.gz.md5', 'r') as infile:
            line = infile.readline()
            assert line == 'a5b04eadcc374613df01fdeb9a426cfa  prefix-abc.txt.gz\n'
            line = infile.readline()
            assert line == ''
        assert not os.path.exists('def.txt')
        assert not os.path.exists('prefix-def.txt')
        assert not os.path.exists('prefix-def.txt.gz')
        assert not os.path.exists('prefix-def.txt.gz.md5')
        assert os.path.exists('hij.txt')
        assert os.path.exists('prefix-hij.txt')
        assert os.path.exists('prefix-hij.txt.gz')
        assert os.path.exists('prefix-hij.txt.gz.md5')
        with open('prefix-hij.txt.gz.md5', 'r') as infile:
            line = infile.readline()
            assert line == 'ea21f0800b4fec21e86cde364080a198  prefix-hij.txt.gz\n'
            line = infile.readline()
            assert line == ''


def test_rename_renaming_nomd5(testdir, mock_testclass):
    src_names = Path(__file__).parent.joinpath('names.txt')
    runner = CliRunner()
    with runner.isolated_filesystem():
        names = 'names.txt'
        copyfile(src_names, names)
        Path('test.txt').touch()
        Path('prefix-test.txt').touch()
        Path('prefix-test.txt.gz').touch()
        with open('prefix-test.txt.gz.md5', 'w') as outfile:
            outfile.write('a5b04eadcc374613df01fdeb9a426cfa  prefix-test.txt.gz\n')
        Path('def.txt').touch()
        Path('prefix-def.txt').touch()
        Path('prefix-def.txt.gz').touch()
        with open('prefix-def.txt.gz.md5', 'w') as outfile:
            outfile.write('ea21f0800b4fec21e86cde364080a198  prefix-def.txt.gz\n')
        result = runner.invoke(rn.rename, ['--names', names, '--no-md5'])
        print (result.output)
        assert result.exit_code == 0
        assert not os.path.exists('test.txt')
        assert not os.path.exists('prefix-test.txt')
        assert not os.path.exists('prefix-test.txt.gz')
        assert not os.path.exists('prefix-test.txt.gz.md5')
        assert os.path.exists('abc.txt')
        assert os.path.exists('prefix-abc.txt')
        assert os.path.exists('prefix-abc.txt.gz')
        assert os.path.exists('prefix-abc.txt.gz.md5')
        with open('prefix-abc.txt.gz.md5', 'r') as infile:
            line = infile.readline()
            assert line == 'a5b04eadcc374613df01fdeb9a426cfa  prefix-test.txt.gz\n'
            line = infile.readline()
            assert line == ''
        assert not os.path.exists('def.txt')
        assert not os.path.exists('prefix-def.txt')
        assert not os.path.exists('prefix-def.txt.gz')
        assert not os.path.exists('prefix-def.txt.gz.md5')
        assert os.path.exists('hij.txt')
        assert os.path.exists('prefix-hij.txt')
        assert os.path.exists('prefix-hij.txt.gz')
        assert os.path.exists('prefix-hij.txt.gz.md5')
        with open('prefix-hij.txt.gz.md5', 'r') as infile:
            line = infile.readline()
            assert line == 'ea21f0800b4fec21e86cde364080a198  prefix-def.txt.gz\n'
            line = infile.readline()
            assert line == ''


def test_rename_renaming_dry(testdir, mock_testclass):
    src_names = Path(__file__).parent.joinpath('names.txt')
    runner = CliRunner()
    with runner.isolated_filesystem():
        names = 'names.txt'
        copyfile(src_names, names)
        Path('test.txt').touch()
        Path('prefix-test.txt').touch()
        Path('prefix-test.txt.gz').touch()
        with open('prefix-test.txt.gz.md5', 'w') as outfile:
            outfile.write('a5b04eadcc374613df01fdeb9a426cfa  prefix-test.txt.gz\n')
        Path('def.txt').touch()
        Path('prefix-def.txt').touch()
        Path('prefix-def.txt.gz').touch()
        with open('prefix-def.txt.gz.md5', 'w') as outfile:
            outfile.write('ea21f0800b4fec21e86cde364080a198  prefix-def.txt.gz\n')
        result = runner.invoke(rn.rename, ['--names', names, '--dry'])
        print (result.output)
        assert result.exit_code == 0
        assert os.path.exists('test.txt')
        assert os.path.exists('prefix-test.txt')
        assert os.path.exists('prefix-test.txt.gz')
        assert os.path.exists('prefix-test.txt.gz.md5')
        assert not os.path.exists('abc.txt')
        assert not os.path.exists('prefix-abc.txt')
        assert not os.path.exists('prefix-abc.txt.gz')
        assert not os.path.exists('prefix-abc.txt.gz.md5')
        with open('prefix-test.txt.gz.md5', 'r') as infile:
            line = infile.readline()
            assert line == 'a5b04eadcc374613df01fdeb9a426cfa  prefix-test.txt.gz\n'
            line = infile.readline()
            assert line == ''
        assert os.path.exists('def.txt')
        assert os.path.exists('prefix-def.txt')
        assert os.path.exists('prefix-def.txt.gz')
        assert os.path.exists('prefix-def.txt.gz.md5')
        assert not os.path.exists('hij.txt')
        assert not os.path.exists('prefix-hij.txt')
        assert not os.path.exists('prefix-hij.txt.gz')
        assert not os.path.exists('prefix-hij.txt.gz.md5')
        with open('prefix-def.txt.gz.md5', 'r') as infile:
            line = infile.readline()
            assert line == 'ea21f0800b4fec21e86cde364080a198  prefix-def.txt.gz\n'
            line = infile.readline()
            assert line == ''


def test_rename_stripstart(testdir, mock_testclass):
    src_names = Path(__file__).parent.joinpath('names.txt')
    runner = CliRunner()
    with runner.isolated_filesystem():
        names = 'names.txt'
        copyfile(src_names, names)
        Path('prefix-test.txt.gz').touch()
        with open('prefix-test.txt.gz.md5', 'w') as outfile:
            outfile.write('a5b04eadcc374613df01fdeb9a426cfa  prefix-test.txt.gz\n')
        Path('prefix-def.txt.gz').touch()
        with open('prefix-def.txt.gz.md5', 'w') as outfile:
            outfile.write('ea21f0800b4fec21e86cde364080a198  prefix-def.txt.gz\n')
        result = runner.invoke(rn.rename, ['--names', names, '--strip-start'])
        print (result.output)
        assert result.exit_code == 0
        assert not os.path.exists('test.txt')
        assert not os.path.exists('prefix-test.txt')
        assert not os.path.exists('prefix-test.txt.gz')
        assert not os.path.exists('prefix-test.txt.gz.md5')
        assert os.path.exists('abc.txt.gz')
        assert os.path.exists('abc.txt.gz.md5')
        with open('abc.txt.gz.md5', 'r') as infile:
            line = infile.readline()
            assert line == 'a5b04eadcc374613df01fdeb9a426cfa  abc.txt.gz\n'
            line = infile.readline()
            assert line == ''
        assert not os.path.exists('def.txt')
        assert not os.path.exists('prefix-def.txt')
        assert not os.path.exists('prefix-def.txt.gz')
        assert not os.path.exists('prefix-def.txt.gz.md5')
        assert os.path.exists('hij.txt.gz')
        assert os.path.exists('hij.txt.gz.md5')
        with open('hij.txt.gz.md5', 'r') as infile:
            line = infile.readline()
            assert line == 'ea21f0800b4fec21e86cde364080a198  hij.txt.gz\n'
            line = infile.readline()
            assert line == ''
