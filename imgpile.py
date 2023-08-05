import logging
import os
import re
import sqlite3
import subprocess
import sys


logger = logging.getLogger('imgpile')


def crawl_exifdata(roots):
    linere = re.compile('^(?P<name>.+\S)\s+:\s+(?P<value>\S.+)$')
    names = ('File Name', 'File Type', 'Image Width', 'Image Height', 'Date/Time Original', 'Create Date')
    for root in roots:
        for (dirpath, dirnames, filenames) in os.walk(root):
            logger.info('starting directory %s', dirpath)
            for filename in filenames:
                path = os.path.join(dirpath, filename)
                process = subprocess.run(('exiftool', path), capture_output=True)
                exifdata = {'path': path, 'returncode': process.returncode}
                if 0 == process.returncode:
                    for line in str(process.stdout).split('\\n'):
                        match = linere.match(line)
                        if match is not None:
                            name = match.group('name')
                            if name in names:
                                exifdata[name] = match.group('value')
                else:
                    logger.error('%s returncode %d: %s', path, process.returncode, process.stderr)
                yield exifdata


def main():
    conn = sqlite3.connect('exifdata.db')
    c = conn.cursor()
    # c.execute('CREATE TABLE exifdata(path PRIMARY KEY, returncode, filename, filetype, width, height, datetime, createdate)')
    # conn.commit()
    for exifdata in crawl_exifdata(sys.argv[1:]):
        t = (
                exifdata.get('path'),
                exifdata.get('returncode'),
                exifdata.get('File Name'),
                exifdata.get('File Type'),
                exifdata.get('Image Width'),
                exifdata.get('Image Height'),
                exifdata.get('Date/Time Original'),
                exifdata.get('Create Date'),
        )
        try:
            c.execute('INSERT INTO exifdata VALUES(?, ?, ?, ?, ?, ?, ?, ?)', t)
            conn.commit()
        except sqlite3.IntegrityError:
            continue

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
