import requests
from json.decoder import JSONDecodeError
import logging
import os
from typing import List
from urllib.parse import urlparse


logger = logging.getLogger(__name__)


def main():
    url = os.getenv('tw165', None)
    if not url:
        logger.critical('URL NOT SET')
        return
    r = requests.get(url)
    if r.status_code != 200:
        logger.critical('Fetch Data Err')
        return

    try:
        r_json = r.json()['result']['records']
    except (JSONDecodeError, KeyError):
        logger.critical('Parse JSON Err')
        raise

    domains = dict.fromkeys([
        urlparse('http://'+row['WEBURL']).hostname
        for row in r_json[1:]
    ])

    filename = 'TW165.txt'
    with open(filename, 'w') as f:
        f.write('\n'.join(domains.keys()))

if __name__ == '__main__':
    main()
