import logging
import subprocess


def sort(bam_input, bam_output, threads=None):
    """Sorts BAM file by location."""
    cmd = ['samtools', 'sort']
    if not threads is None and threads > 1:
        cmd.extend(['--threads', str(threads - 1)])
    cmd.extend(['-o', bam_output, bam_input])
    logging.debug('Running {}'.format(cmd))
    subprocess.run(cmd, check=True)


def sort_by_readname(bam_input, bam_output, threads=None):
    """Sorts BAM file by read name."""
    cmd = ['samtools', 'sort', '-n']
    if not threads is None and threads > 1:
        cmd.extend(['--threads', str(threads - 1)])
    cmd.extend(['-o', bam_output, bam_input])
    logging.debug('Running {}'.format(cmd))
    subprocess.run(cmd, check=True)
