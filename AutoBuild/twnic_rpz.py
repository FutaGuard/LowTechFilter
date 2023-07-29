import requests
import json
import logging
from json.decoder import JSONDecodeError
import sys
from typing import List

logger = logging.getLogger(__name__)


def main():
    r = requests.get('https://rpz.twnic.tw/e.html')
    if r.status_code != 200:
        logger.critical('Fetch Data Err')
        sys.exit(1)

    # split text from <script> tag
    raw: str = r.text.split('<script>')[1].split(';')[0].split('= ')[1]
    parse_data: List[dict] = [dict()]
    try:
        parse_data = json.loads(raw)
    except JSONDecodeError:
        logger.critical('Parse JSON Err')
        sys.exit(1)

    output = [domain for in_dic in parse_data for domain in in_dic['domains']]
    with open('TWNIC-RPZ.txt', 'w') as f:
        f.write(''.join(f'||{e}^\n' for e in output))


if __name__ == '__main__':
    main()
