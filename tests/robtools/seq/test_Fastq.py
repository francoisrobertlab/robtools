import logging

from robtools.seq import Fastq


def create_file(output):
    with open(output, 'w') as outfile:
        outfile.write('test')


def test_fastq_1(testdir):
    sample = 'PORL2A'
    fastq = 'PORL2A_1.fastq'
    create_file(fastq)
    assert Fastq.fastq(sample, 1) == fastq


def test_fastq_1_default(testdir):
    sample = 'PORL2A'
    fastq = 'PORL2A_1.fastq'
    create_file(fastq)
    assert Fastq.fastq(sample) == fastq


def test_fastq_1gz(testdir):
    sample = 'PORL2A'
    fastq = 'PORL2A_1.fastq.gz'
    create_file(fastq)
    assert Fastq.fastq(sample, 1) == fastq


def test_fastq_R1(testdir):
    sample = 'PORL2A'
    fastq = 'PORL2A_R1.fastq'
    create_file(fastq)
    assert Fastq.fastq(sample, 1) == fastq


def test_fastq_R1_gz(testdir):
    sample = 'PORL2A'
    fastq = 'PORL2A_R1.fastq.gz'
    create_file(fastq)
    assert Fastq.fastq(sample, 1) == fastq


def test_fastq_1_suffix(testdir):
    sample = 'PORL2A'
    fastq = 'PORL2A-suf_1.fastq'
    create_file(fastq)
    assert Fastq.fastq(sample, 1, '-suf') == fastq


def test_fastq_1gz_suffix(testdir):
    sample = 'PORL2A'
    fastq = 'PORL2A-suf_1.fastq.gz'
    create_file(fastq)
    assert Fastq.fastq(sample, 1, '-suf') == fastq


def test_fastq_R1_suffix(testdir):
    sample = 'PORL2A'
    fastq = 'PORL2A-suf_R1.fastq'
    create_file(fastq)
    assert Fastq.fastq(sample, 1, '-suf') == fastq


def test_fastq_R1_gz_suffix(testdir):
    sample = 'PORL2A'
    fastq = 'PORL2A-suf_R1.fastq.gz'
    create_file(fastq)
    assert Fastq.fastq(sample, 1, '-suf') == fastq


def test_fastq_1_notexists(testdir):
    sample = 'PORL2A'
    assert Fastq.fastq(sample, 1) == None


def test_fastq_2(testdir):
    sample = 'PORL2A'
    fastq = 'PORL2A_2.fastq'
    create_file(fastq)
    assert Fastq.fastq(sample, 2) == fastq


def test_fastq_2gz(testdir):
    sample = 'PORL2A'
    fastq = 'PORL2A_2.fastq.gz'
    create_file(fastq)
    assert Fastq.fastq(sample, 2) == fastq


def test_fastq_R2(testdir):
    sample = 'PORL2A'
    fastq = 'PORL2A_R2.fastq'
    create_file(fastq)
    assert Fastq.fastq(sample, 2) == fastq


def test_fastq_R2_gz(testdir):
    sample = 'PORL2A'
    fastq = 'PORL2A_R2.fastq.gz'
    create_file(fastq)
    assert Fastq.fastq(sample, 2) == fastq


def test_fastq_2_suffix(testdir):
    sample = 'PORL2A'
    fastq = 'PORL2A-suf_2.fastq'
    create_file(fastq)
    assert Fastq.fastq(sample, 2, '-suf') == fastq


def test_fastq_2gz_suffix(testdir):
    sample = 'PORL2A'
    fastq = 'PORL2A-suf_2.fastq.gz'
    create_file(fastq)
    assert Fastq.fastq(sample, 2, '-suf') == fastq


def test_fastq_R2_suffix(testdir):
    sample = 'PORL2A'
    fastq = 'PORL2A-suf_R2.fastq'
    create_file(fastq)
    assert Fastq.fastq(sample, 2, '-suf') == fastq


def test_fastq_R2_gz_suffix(testdir):
    sample = 'PORL2A'
    fastq = 'PORL2A-suf_R2.fastq.gz'
    create_file(fastq)
    assert Fastq.fastq(sample, 2, '-suf') == fastq


def test_fastq_2_notexists(testdir):
    sample = 'PORL2A'
    assert Fastq.fastq(sample, 2) == None
