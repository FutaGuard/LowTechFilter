import requests
from requests.auth import HTTPBasicAuth
from json.decoder import JSONDecodeError
import logging
import os
from typing import List
from urllib.parse import urlparse


logger = logging.getLogger(__name__)


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
        urlparse('http://'+row['WEBURL']).hostname
        for row in r_json[1:]
    ])

    r = fetchdata(csvurl)
    domains.update(dict.fromkeys(
        [
            x.split(',')[1]
            for x in r.text.splitlines()[2:]
        ]
    ))

    filename = 'TW165.txt'
    with open(filename, 'w') as f:
        f.write('\n'.join(domains.keys()))

if __name__ == '__main__':
    main()
