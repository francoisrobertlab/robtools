import click
import yaml


@click.command()
@click.option('-p', '--project', type=click.Path(exists=True), default='project.yml', show_default=True,
              help='Distiller project file.')
def distillerresolutions(project):
    """Prints resolutions from distiller-nf project.xml's file one resolution per line"""
    with open(project) as project_in:
        config = yaml.safe_load(project_in)
    resolutions = config['bin']['resolutions']
    print('\n'.join([str(resolution) for resolution in resolutions]))


if __name__ == '__main__':
    distillerresolutions()
