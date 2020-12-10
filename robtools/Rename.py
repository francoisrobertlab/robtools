import glob
import os
import shutil
import tempfile

import click


@click.command()
@click.option('--names', '-n', type=click.Path(exists=True), help='Files to rename. In first column is the old name, in the second is the new name.')
@click.option('--md5/--no-md5', default=True, help='Also change the file name in the .md5 file that is associated.')
@click.option('--strip-start/--no-strip-start', default=False, help='Strip the filename before new name.')
@click.option('--dry/--no-dry', default=False, help='Do not rename files.')
def rename(names, md5, strip_start, dry):
    rename_(names, md5, strip_start, dry)


def rename_(names, md5=True, strip_start=False, dry=False):
    '''Rename files.'''
    with open(names, 'r') as infile:
        for line in infile:
            if line.startswith('#'):
                continue
            columns = line.rstrip('\r\n').split('\t')
            for file in sorted(glob.glob('*' + columns[0] + '*')):
                index = file.index(columns[0])
                output = ('' if strip_start else file[:index]) + columns[1] + file[index + len(columns[0]):]
                print ('rename file {} to {}'.format(file, output))
                if not dry:
                    os.rename(file, output)
                if md5:
                    md5_file = file + '.md5'
                    if os.path.isfile(md5_file):
                        print ('renaming {} to {} in md5 file {}'.format(file, output, md5_file))
                        rename_in_md5(md5_file, output, dry)
        

def rename_in_md5(md5, replacement, dry=False):
    md5_temp_o, md5_temp = tempfile.mkstemp(suffix='.md5')
    with open(md5, 'r') as infile, open(md5_temp_o, 'w') as outfile:
        for line in infile:
            columns = line.rstrip('\r\n').split()
            if len(columns) == 2:
                columns[1] = replacement
                outfile.write('  '.join(columns))
                outfile.write('\n')
    if not dry:
        shutil.copyfile(md5_temp, md5)
    else:
        os.remove(md5_temp)


if __name__ == '__main__':
    rename()
