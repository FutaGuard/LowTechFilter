import re
import sys
from datetime import datetime, timedelta, timezone

tz = timezone(timedelta(hours=+8))
today = datetime.now(tz).date()

args = sys.argv
if len(args) != 2:
    print('Got Empty Arguments')
    sys.exit(1)

files = args[-1]

with open(files, 'r') as f:
    pattern = r'(?<=Version: )(\d+\.\d+\.)(\d+)'
    read_file = f.read()
    first = '\n'.join(read_file.splitlines()[:5])
    version = re.findall(pattern, first, re.MULTILINE)[0]
    dt = datetime.strptime(version[0], '%Y.%m%d.').date()
    newversion = today.strftime('%Y.%m%d.')

    if dt != today:
        newversion += '1'
    else:
        newversion += str(int(version[1])+1)

    with open(files, 'w') as f_:
        f_.write(read_file.replace(''.join(version), newversion))
