import logging
import os
from pathlib import Path
import pytest
from shutil import copyfile
import subprocess
from unittest.mock import MagicMock, ANY

import click
from click.testing import CliRunner
from robtools import Fixmd5 as fm


@pytest.fixture
def mock_testclass():
    fixmd5_ = fm.fixmd5_
    yield 
    fm.fixmd5_ = fixmd5_
    
    
def test_fixmd5(testdir, mock_testclass):
    src_names = Path(__file__).parent.joinpath('names.txt')
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('prefix-test.txt.gz.md5', 'w') as outfile:
            outfile.write('a5b04eadcc374613df01fdeb9a426cfa  /home/abc/test.txt.gz\n')
        with open('prefix-def.txt.gz.md5', 'w') as outfile:
            outfile.write('ea21f0800b4fec21e86cde364080a198  def.txt.gz\n')
        result = runner.invoke(fm.fixmd5)
        print (result.output)
        assert result.exit_code == 0
        assert os.path.exists('prefix-test.txt.gz.md5')
        with open('prefix-test.txt.gz.md5', 'r') as infile:
            line = infile.readline()
            assert line == 'a5b04eadcc374613df01fdeb9a426cfa  prefix-test.txt.gz\n'
            line = infile.readline()
            assert line == ''
        assert os.path.exists('prefix-def.txt.gz.md5')
        with open('prefix-def.txt.gz.md5', 'r') as infile:
            line = infile.readline()
            assert line == 'ea21f0800b4fec21e86cde364080a198  prefix-def.txt.gz\n'
            line = infile.readline()
            assert line == ''


def test_fixmd5_single(testdir, mock_testclass):
    src_names = Path(__file__).parent.joinpath('names.txt')
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('prefix-test.txt.gz.md5', 'w') as outfile:
            outfile.write('a5b04eadcc374613df01fdeb9a426cfa  /home/abc/test.txt.gz\n')
        with open('prefix-def.txt.gz.md5', 'w') as outfile:
            outfile.write('ea21f0800b4fec21e86cde364080a198  def.txt.gz\n')
        result = runner.invoke(fm.fixmd5, ['-f', '*test*.md5'])
        print (result.output)
        assert result.exit_code == 0
        assert os.path.exists('prefix-test.txt.gz.md5')
        with open('prefix-test.txt.gz.md5', 'r') as infile:
            line = infile.readline()
            assert line == 'a5b04eadcc374613df01fdeb9a426cfa  prefix-test.txt.gz\n'
            line = infile.readline()
            assert line == ''
        assert os.path.exists('prefix-def.txt.gz.md5')
        with open('prefix-def.txt.gz.md5', 'r') as infile:
            line = infile.readline()
            assert line == 'ea21f0800b4fec21e86cde364080a198  def.txt.gz\n'
            line = infile.readline()
            assert line == ''


def test_fixmd5_dry(testdir, mock_testclass):
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open('prefix-test.txt.gz.md5', 'w') as outfile:
            outfile.write('a5b04eadcc374613df01fdeb9a426cfa  /home/abc/test.txt.gz\n')
        with open('prefix-def.txt.gz.md5', 'w') as outfile:
            outfile.write('ea21f0800b4fec21e86cde364080a198  def.txt.gz\n')
        result = runner.invoke(fm.fixmd5, ['--dry'])
        print (result.output)
        assert result.exit_code == 0
        assert os.path.exists('prefix-test.txt.gz.md5')
        with open('prefix-test.txt.gz.md5', 'r') as infile:
            line = infile.readline()
            assert line == 'a5b04eadcc374613df01fdeb9a426cfa  /home/abc/test.txt.gz\n'
            line = infile.readline()
            assert line == ''
        assert os.path.exists('prefix-def.txt.gz.md5')
        with open('prefix-def.txt.gz.md5', 'r') as infile:
            line = infile.readline()
            assert line == 'ea21f0800b4fec21e86cde364080a198  def.txt.gz\n'
            line = infile.readline()
            assert line == ''
