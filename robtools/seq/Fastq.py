import os
import re


def fastq(sample, read=1, suffix=''):
    '''Returns existing FASTQ file for sample - read 1 or read 2, defaults to read 1.'''
    files = [f for f in os.listdir('.') if re.match('^' + re.escape(sample + suffix) + r'_R?' + str(read) + r'\.fastq(\.gz)?$', f)]
    if len(files) == 0:
        return None
    else:
        return files[0]
