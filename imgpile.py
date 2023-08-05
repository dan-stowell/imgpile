import logging
import os
import re
import subprocess
import sys


logger = logging.getLogger('imgpile')


def crawl_exifdata(roots):
    linere = re.compile('^(?P<name>.+\S)\s+:\s+(?P<value>\S.+)$')
    names = ('File Type', 'Image Width', 'Image Height', 'Date/Time Original', 'Create Date')
    for root in roots:
        for (dirpath, dirnames, filenames) in os.walk(root):
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
    for exifdata in crawl_exifdata(sys.argv[1:]):
        logger.info(exifdata)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
