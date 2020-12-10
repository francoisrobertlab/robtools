import click

from robtools import Bam2Bed, Bowtie2, Bwa, CenterAnnotations, ChipexoQual, Download, FilterBam, Fixmd5, GenomeCoverage, IgnoreStrand, Intersect, IntersectAnnotations, Merge, MergeBam, MergeBigwigs, Plot2do, RemoveSecondMate, Rename, ShiftAnnotations, SlowSplit, Split, Statistics, Vap


@click.group()
def robtools():
    pass


robtools.add_command(Bam2Bed.bam2bed)
robtools.add_command(Bowtie2.bowtie2)
robtools.add_command(Bwa.bwa)
robtools.add_command(CenterAnnotations.centerannotations)
robtools.add_command(ChipexoQual.chipexoqual)
robtools.add_command(Download.download)
robtools.add_command(FilterBam.filterbam)
robtools.add_command(Fixmd5.fixmd5)
robtools.add_command(GenomeCoverage.genomecov)
robtools.add_command(IgnoreStrand.ignorestrand)
robtools.add_command(Intersect.intersect)
robtools.add_command(IntersectAnnotations.intersectannotations)
robtools.add_command(Merge.merge)
robtools.add_command(MergeBam.mergebam)
robtools.add_command(MergeBigwigs.mergebw)
robtools.add_command(Plot2do.plot2do)
robtools.add_command(RemoveSecondMate.removesecondmate)
robtools.add_command(Rename.rename)
robtools.add_command(ShiftAnnotations.shiftannotations)
robtools.add_command(SlowSplit.slowsplit)
robtools.add_command(Split.split)
robtools.add_command(Statistics.statistics)
robtools.add_command(Vap.vap)

if __name__ == '__main__':
   robtools()
