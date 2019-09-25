import logging
import os
import subprocess

import RunBwa
import click
import pandas as pd


@click.command()
@click.option('--samples', '-s', type=click.Path(exists=True), default='samples.txt',
              help='Sample names listed one sample name by line.'
              ' An SRR id can be provided (tab-separated) to download the FASTQ file automatically, otherwise FASTQ file must be provided.')
@click.option('--index', '-i', type=int, default=None,
              help='Index of sample to process in samples file.')
def main(samples, index):
    '''Download reads of all samples.'''
    logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    sample_columns = pd.read_csv(samples, header=None, sep='\t', comment='#')
    if index != None:
        sample_columns = [sample_columns.iloc[index]]
    for columns in sample_columns:
        sample = columns[0]
        srr = columns[1] if len(columns) > 1 else None
        download(sample, srr)


def download(sample, srr):
    '''Download reads of a sample.'''
    fastq = sample
    fastq_exists = RunBwa.fastq(fastq, 1)
    if fastq_exists is None and srr:
        print ('Downloading FASTQ for sample {} with SRR {}'.format(sample, srr))
        fastq1 = fastq + '_1.fastq'
        fastq2 = fastq + '_2.fastq'
        srr_output1 = srr + '_1.fastq'
        srr_output2 = srr + '_2.fastq'
        cmd = ['fasterq-dump', '--split-files', srr];
        logging.debug('Running {}'.format(cmd))
        subprocess.call(cmd)
        os.rename(srr_output1, fastq1)
        if os.path.isfile(srr_output2):
            os.rename(srr_output2, fastq2)


if __name__ == '__main__':
    main()
