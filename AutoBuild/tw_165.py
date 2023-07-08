import requests
from json.decoder import JSONDecodeError
import logging
import os
from typing import List
from urllib.parse import urlparse


logger = logging.getLogger(__name__)


def main():
    url = os.getenv('env.TW165', None)
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
    
    # check if file exists
    filename = 'TW165.txt'
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            pass
    
    added_list: List[str] = []

    with open(filename, 'r') as f:
        read_ = f.read().splitlines()
        for row in r_json[1:]:
            domain = urlparse('http://'+row['WEBURL']).hostname
            if domain not in read_:
                added_list.append(domain)
    
    with open(filename, 'a+') as f:
        f.write('\n')
        f.write(
            '\n'.join(e for e in added_list)
            )

if __name__ == '__main__':
    main()