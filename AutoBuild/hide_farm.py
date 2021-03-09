import os
from datetime import datetime, timedelta, timezone

tz = timezone(timedelta(hours=+8))

domain_list = ''
with open('../nofarm_hosts.txt', 'r') as files:
    for domains in files.read().split('\n'):
        if domains[1] != '!':
            domain = domains[2:-1]
            domain_list += 'google.*##div.g:has(div[data-hveid] a[href*="{domain}"])\n'.format(
                domain=domain
            )

if not os.path.exists('../hide_farm_from_search.txt'):
    with open('../hide_farm_from_search.txt', 'w') as files:
        pass

with open('../hide_farm_from_search.txt', 'r') as orig:
    version, ver_dt = '', ''
    try:
        version = orig.read().split('\n')[2].split(': ')[1]
        ver_dt = datetime.strptime(version[:-3], '%Y.%m%d').date()
    except IndexError:
        pass

    now = datetime.now(tz)
    v = now.strftime('%Y.%m%d.')
    if now.date() != ver_dt:
        v += '01'
    else:
        v += str(int(version[-2:])+1).zfill(2)

head = '[Adblock Plus]\n' \
       '! Title: hide farm content from google\n' \
       '! Version: {version}\n' \
       '! Expires: 1 hour\n' \
       '! Homepage: https://t.me/adguard_tw\n' \
       '! ----------------------------------------------------------------------\n'.format(
           version=v
       )

with open('../hide_farm_from_search.txt', 'w') as files:
    files.write(head + domain_list)

