import logging

import pandas as pd


def columns(file):
    '''Parses file.'''
    all_columns = [];
    with open(file, 'r') as infile:
        for line in infile:
            line = line.rstrip('\r\n')
            if not line.startswith('#'):
                all_columns.append(line.split('\t'))
    return all_columns


def first(file):
    '''Parses first column of file.'''
    first_column = [];
    with open(file, 'r') as infile:
        for line in infile:
            line = line.rstrip('\r\n')
            if not line.startswith('#'):
                first_column.append(line.split('\t')[0])
    return first_column
