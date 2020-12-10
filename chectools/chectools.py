import click

from chectools import DyadPosition


@click.group()
def chectools():
    pass


chectools.add_command(DyadPosition.dyadposition)

if __name__ == '__main__':
   chectools()
