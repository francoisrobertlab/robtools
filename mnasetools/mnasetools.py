import click

from mnasetools import DyadCoverage, DyadStatistics, FitDoubleGaussian, FitGaussian, FitGaussians, FirstDyadPosition


@click.group()
def mnasetools():
    pass


mnasetools.add_command(DyadCoverage.dyadcov)
mnasetools.add_command(DyadStatistics.dyadstatistics)
mnasetools.add_command(FitDoubleGaussian.fitdoublegaussian)
mnasetools.add_command(FitGaussian.fitgaussian)
mnasetools.add_command(FitGaussians.fitgaussians)
mnasetools.add_command(FirstDyadPosition.firstdyadposition)

if __name__ == '__main__':
   mnasetools()
