import click

from robtools import Bam2Bed
from robtools import Bowtie2
from robtools import Bwa
from robtools import CenterAnnotations
from robtools import ChipexoQual
from robtools import DistillerResolutions
from robtools import Download
from robtools import FilterBam
from robtools import Fixmd5
from robtools import GenomeCoverage
from robtools import IgnoreStrand
from robtools import Intersect
from robtools import IntersectAnnotations
from robtools import KeepRandomReads
from robtools import KeepRandomReadsBam
from robtools import Merge
from robtools import MergeBam
from robtools import MergeBigwigs
from robtools import Pairs2Hic
from robtools import Plot2do
from robtools import PrintSample
from robtools import RemoveSecondMate
from robtools import Rename
from robtools import ShiftAnnotations
from robtools import Siqchip
from robtools import SiqchipBed
from robtools import SlowSplit
from robtools import Split
from robtools import Statistics
from robtools import Trimmomatic
from robtools import Vap


@click.group()
def robtools():
    pass


robtools.add_command(Bam2Bed.bam2bed)
robtools.add_command(Bowtie2.bowtie2)
robtools.add_command(Bwa.bwa)
robtools.add_command(CenterAnnotations.centerannotations)
robtools.add_command(ChipexoQual.chipexoqual)
robtools.add_command(DistillerResolutions.distillerresolutions)
robtools.add_command(Download.download)
robtools.add_command(FilterBam.filterbam)
robtools.add_command(Fixmd5.fixmd5)
robtools.add_command(GenomeCoverage.genomecov)
robtools.add_command(IgnoreStrand.ignorestrand)
robtools.add_command(Intersect.intersect)
robtools.add_command(IntersectAnnotations.intersectannotations)
robtools.add_command(KeepRandomReads.keeprandomreads)
robtools.add_command(KeepRandomReadsBam.keeprandomreadsbam)
robtools.add_command(Merge.merge)
robtools.add_command(MergeBam.mergebam)
robtools.add_command(MergeBigwigs.mergebw)
robtools.add_command(Pairs2Hic.pairs2hic)
robtools.add_command(Plot2do.plot2do)
robtools.add_command(PrintSample.printsample)
robtools.add_command(RemoveSecondMate.removesecondmate)
robtools.add_command(Rename.rename)
robtools.add_command(ShiftAnnotations.shiftannotations)
robtools.add_command(Siqchip.siqchip)
robtools.add_command(SiqchipBed.siqchipbed)
robtools.add_command(SlowSplit.slowsplit)
robtools.add_command(Split.split)
robtools.add_command(Statistics.statistics)
robtools.add_command(Trimmomatic.trimmomatic)
robtools.add_command(Vap.vap)

if __name__ == '__main__':
    robtools()
