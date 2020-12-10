import logging

import pandas as pd


def columns(samples):
    '''Parses samples file.'''
    columns = pd.read_csv(samples, header=None, sep='\t', comment='#')
    return columns.values.tolist()


def first(samples):
    '''Parses first column of samples file.'''
    first = pd.read_csv(samples, header=None, sep='\t', comment='#')[0]
    return first.tolist()
