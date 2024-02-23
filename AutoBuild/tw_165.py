import logging
import os
import re
from json.decoder import JSONDecodeError
from urllib.parse import urlparse

import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)
IP_PATTERN = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'


def exclude_list(domain: str) -> bool:
    exclude = ['google.com']
    for e in exclude:
        if domain.endswith(e):
            return True
    return False

def is_pure_ip(domain: str) -> bool:
    return True if re.match(IP_PATTERN, domain) else False


def main():
    auth = os.getenv('auth', None)
    jsonurl = os.getenv('tw165json', None)
    csvurl = os.getenv('tw165csv', None)
    if not jsonurl or not csvurl:
        logger.critical('URL NOT SET')
        return
    if not auth:
        logger.critical('AUTH NOT SET')
        return

    user, passwd = auth.split(':')
    basic = HTTPBasicAuth(user, passwd)

    def fetchdata(url):
        r = requests.get(url, auth=basic)
        if r.status_code != 200:
            logger.critical('Fetch Data Err')
            return
        return r

    r = fetchdata(jsonurl)
    try:
        r_json = r.json()['result']['records']
    except (JSONDecodeError, KeyError):
        logger.critical('Parse JSON Err')
        raise

    domains = dict.fromkeys([
        urlparse(row['WEBURL']).hostname if row['WEBURL'].startswith('http') else urlparse(
            'http://' + row['WEBURL']).hostname
        for row in r_json[1:]
    ])

    r = fetchdata(csvurl)
    domains.update(dict.fromkeys(
        [
            urlparse(x.split(',')[1]).hostname if x.split(',')[1].startswith('http') else urlparse(
                'http://' + x.split(',')[1]).hostname
            for x in r.text.splitlines()[2:]
        ]
    ))

    # 移除純 IP & 移除允許清單
    domains = {k: v for k, v in domains.items() if not is_pure_ip(k) \
               and not exclude_list(k)}
    
    filename = 'TW165.txt'
    with open(filename, 'w') as f:
        f.write('\n'.join(domains.keys()))


if __name__ == '__main__':
    main()
