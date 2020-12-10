import glob
import os
import shutil
import tempfile

import click


@click.command()
@click.option('--files', '-f', default='*.md5', show_default=True, help='MD5 filename(s) to fix. You can use * as a wildcard.')
@click.option('--dry/--no-dry', default=False, help='Do not fix files, only show fix messages.')
def fixmd5(files, dry):
    fixmd5_(files, dry)


def fixmd5_(files='*.md5', dry=False):
    '''Fix filename in md5 files.'''
    for file in sorted(glob.glob(files)):
        replacement = os.path.splitext(os.path.basename(file))[0]
        print ('use {} as filename in md5 file {}'.format(replacement, file))
        md5_temp_o, md5_temp = tempfile.mkstemp(suffix='.md5')
        with open(file, 'r') as infile, open(md5_temp_o, 'w') as outfile:
            for line in infile:
                columns = line.rstrip('\r\n').split()
                if len(columns) == 2:
                    columns[1] = replacement
                    outfile.write('  '.join(columns))
                    outfile.write('\n')
        if not dry:
            shutil.copyfile(md5_temp, file)
        else:
            os.remove(md5_temp)


if __name__ == '__main__':
    fixmd5()
