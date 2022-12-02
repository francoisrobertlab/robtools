import glob
import gzip
import logging
import os.path
import subprocess
import tempfile

import click
import sys
import yaml


@click.command(context_settings=dict(ignore_unknown_options=True, ))
@click.option('--project', '-p', type=click.Path(exists=True), default="project.yml", show_default=True,
              help="Distiller project file.")
@click.option('--juicer', '-j', type=click.Path(exists=True), default="juicer_tools.jar", show_default=True,
              help="Juicer tools jar file from Juicebox.")
@click.option('--input-suffix', '-is', default="*.nodups", show_default=True,
              help="Suffix added to sample/group name in pairs filename for input. Stars are wildcards.")
@click.option('--output-suffix', '-os', default=None,
              help="Suffix added to sample/group name in HIC filename for output.")
@click.option('--output-folder', '-o', type=click.Path(exists=True), default=None,
              help="Output folder.  Defaults to current folder.")
@click.argument('juicer_args', nargs=-1, type=click.UNPROCESSED)
def pairs2hic(project, juicer, input_suffix, output_suffix, output_folder, juicer_args):
    """Converts distiller-nf's pairs file to HIC format"""
    logging.basicConfig(filename='robtools.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    pairs2hic_(project, juicer, input_suffix, output_suffix, output_folder, juicer_args)


def pairs2hic_(project, juicer="juicer_tools.jar", input_suffix="*.nodups", output_suffix=None, output_folder=None,
               juicer_args=()):
    with open(project) as project_in:
        config = yaml.safe_load(project_in)
    samples = list(config['input']['raw_reads_paths'].keys())
    groups = config['input']['library_groups']
    resolutions = config['bin']['resolutions']
    chrom_sizes_path = config['input']['genome']['chrom_sizes_path']
    if not output_folder:
        output_folder = '.'
    folders = []
    if os.path.abspath(os.path.dirname(project)) != os.path.abspath(os.curdir):
        folders.append(os.path.dirname(project))
    folders.append('')
    chromosome_sizes = resolve(os.path.basename(chrom_sizes_path), (
            [os.path.join(os.path.dirname(project), os.path.dirname(chrom_sizes_path))] + folders) if os.path.dirname(
        chrom_sizes_path) != '' else folders)
    if not chromosome_sizes:
        print(f"Could not find genome file {os.path.basename(chrom_sizes_path)}", file=sys.stderr)
        exit(1)
    for sample in samples:
        pairs = resolve(f"{sample}{input_suffix}.pairs.gz", folders)
        if not pairs:
            print(f"Could not find pairs file for sample {sample}", file=sys.stderr)
            continue
        hic = os.path.join(output_folder, f"{sample}{output_suffix if output_suffix else ''}.hic")
        print(f"\n\nConverting pairs file {os.path.basename(pairs)} to HIC {os.path.basename(hic)}")
        pairs_to_hic(pairs, hic, resolutions, chromosome_sizes, juicer, juicer_args)
    for group in groups:
        pairs = [resolve(f"{sample}{input_suffix}.pairs.gz", folders) for sample in groups[group]]
        if None in pairs:
            sample = groups[group][pairs.index(None)]
            print(f"Could not find pairs files for sample {sample} in group {group}", file=sys.stderr)
            continue
        hic = os.path.join(output_folder, f"{group}{output_suffix if output_suffix else ''}.hic")
        print(f"\n\nConverting pairs of group {group} to HIC {os.path.basename(hic)}")
        merged_pairs_o, merged_pairs = tempfile.mkstemp(suffix='.pairs.gz')
        logging.debug(f"before merge_pairs")
        merge_pairs(pairs, merged_pairs)
        logging.debug(f"after merge_pairs")
        pairs_to_hic(merged_pairs, hic, resolutions, chromosome_sizes, juicer, juicer_args)
        logging.debug(f"after pairs_to_hic")
        os.remove(merged_pairs)
    logging.debug(f"finished")


def pairs_to_hic(pairs, hic, resolutions, chromosome_sizes, juicer="juicer_tools.jar", juicer_args=()):
    """Converts pairs file to HIC file"""
    medium_o, medium = tempfile.mkstemp(suffix=".tsv")
    pairs_to_medium(pairs, medium)
    logging.debug(f'Converting medium format {medium} to HIC {hic}')
    cmd = ["java", "-jar", juicer, "pre"] + list(juicer_args)
    cmd.extend(["-r", ','.join([str(resolution) for resolution in resolutions])])
    cmd.extend([medium, hic, chromosome_sizes])
    logging.debug(f'Running {cmd}')
    subprocess.run(cmd, check=True)
    os.remove(medium)


def pairs_to_medium(pairs, medium):
    """Converts pairs file to medium format for juicer"""
    logging.debug(f'Converting pairs {pairs} to medium format {medium}')
    with gzip.open(pairs, 'rt') as pairs_in, open(medium, 'w') as medium_out:
        for line in pairs_in:
            if line.startswith('#'):
                continue
            columns = line.strip('\r\n').split('\t')
            out_columns = [columns[0]]
            out_columns.extend(['0' if columns[5] == '+' else '1', columns[1], columns[2], '0'])
            out_columns.extend(['0' if columns[6] == '+' else '1', columns[3], columns[4], '1'])
            out_columns.extend([columns[8], columns[9]])
            medium_out.write('\t'.join(out_columns))
            medium_out.write('\n')


def resolve(pathname, folders):
    """Return first pathname inside one of the folders"""
    for folder in folders:
        files = glob.glob(os.path.join(folder, '**', pathname), recursive=True)
        if files:
            return os.path.join(files[0])
    return None


def merge_pairs(pairs, outfile):
    """Merge files"""
    merge_o, merge = tempfile.mkstemp(suffix=".tsv")
    logging.debug(f'Merging pairs {pairs} to {merge}')
    with open(merge_o, 'w') as merge_out:
        for file in pairs:
            with gzip.open(file, 'rt') as file_in:
                for line in file_in:
                    if line.startswith('#'):
                        continue
                    merge_out.write(line)
    sort_o, sort = tempfile.mkstemp(suffix=".tsv")
    logging.debug(f'Sorting pairs {merge} to {sort}')
    cmd = ["sort", "-k", "2,2", "-k", "4,4", "-k", "3,3n", "-k", "5,5n", "-o", sort, merge]
    logging.debug(f'Running {cmd}')
    subprocess.run(cmd, check=True)
    os.remove(merge)
    logging.debug(f'Gzip pairs {sort} to {outfile}')
    with gzip.open(outfile, 'wt') as outfile_out, open(sort_o) as sort_in:
        for line in sort_in:
            outfile_out.write(line)
    os.remove(sort)


if __name__ == '__main__':
    pairs2hic()
