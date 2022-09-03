import requests
import re
from datetime import datetime, timedelta, timezone

filterlist = {
    'abp': ['experimental.txt', 'filter.txt'],
    'hosts': ['hosts.txt', 'nofarm_hosts.txt']
}
url = 'https://filter.futa.gg/'
tz = timezone(timedelta(hours=+8))
today = datetime.now(tz).date()

class HEAD:
    abp: str = '[Adblock Plus]\n' \
               '! Title: LowTechFilter {name}\n' \
               '! Version: {version}\n' \
               '! Expires: 1 hour\n' \
               '! Homepage: https://t.me/adguard_tw\n' \
               '! ----------------------------------------------------------------------\n'
    hosts: str = '! FutaHosts\n' \
                '! LowTechFilter {name}\n' \
                '! URL: <https://github.com/FutaGuard/LowTechFilter>\n' \
                '! Version: {version}\n' \
                '! --------------------------------------------------\n'


for category in filterlist:
    for filename in filterlist[category]:
        pattern = r'(?<=Version: )(\d+\.\d+\.)(\d+)'

        r = requests.get(url+filename)
        first = None
        version = None
        if r.status_code != 200:
            pass
        else:
            first = '\n'.join(r.text.splitlines()[:5])

        try:
            version = re.findall(pattern, first, re.MULTILINE)[0]
        except:
            # https://www.ptt.cc/bbs/Battlegirlhs/M.1506615677.A.1A4.html
            version = ('2017.0929.', '1')

        dt = datetime.strptime(version[0], '%Y.%m%d.').date()
        newversion = today.strftime('%Y.%m%d.')
        if dt != today:
            newversion += '1'
        else:
            newversion += str(int(version[1]) + 1)

        with open(f'../{filename}', 'r') as files:
            with open(f'{filename}', 'w') as output:
                heads: str = HEAD().__getattribute__(category)
                news = heads.format(
                    name=filename.split('.')[0].replace('_', ' ').title(),
                    version=newversion
                )
                output.write(news+files.read())