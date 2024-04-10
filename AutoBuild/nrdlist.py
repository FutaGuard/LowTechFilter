import signal
from typing import Dict

import httpx
import arrow
from base64 import b64encode
import pathlib
import logging
import asyncio
from zipfile import ZipFile, BadZipfile
from io import BytesIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Downloader:
    def __init__(self):
        self.base_url = "https://www.whoisds.com//whois-database/newly-registered-domains/{args}/nrd"
        self.base_path = pathlib.Path("nrd")
        self.data: Dict[str, BytesIO] = {}
        if not self.base_path.exists():
            self.base_path.mkdir()

    async def fetch(self, date: arrow.Arrow) -> bool:
        logger.info("Downloading: %s", date.format("YYYY-MM-DD"))
        url = self.base_url.format(
            args=b64encode(date.strftime("%Y-%m-%d.zip").encode()).decode()
        )
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            if r.status_code != 200:
                logger.error("Download failed: %s", url)
                return False
            zip_file = BytesIO(r.content)
            try:
                with ZipFile(zip_file, "r") as zip_obj:
                    # print(zip_obj.read('domain-names.txt'))
                    self.data[date.format("YYYY-MM-DD")] = zip_obj.read(
                        "domain-names.txt"
                    )
            except BadZipfile:
                logger.error("Bad Zipfile: %s", url)
                return False
            return True

    async def write(self):
        sort_date = sorted(self.data.keys(), reverse=True)
        accumulate = ""
        for date in range(len(sort_date)):
            accumulate += self.data[sort_date[date]].decode()
            self.base_path.joinpath(f"past-{date+1}day.txt").write_bytes(
                accumulate.encode()
            )

    def run(self):
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(signal.SIGILL, loop.stop)
        loop.add_signal_handler(signal.SIGINT, loop.stop)
        today = arrow.utcnow()
        task = []

        for i in range(1, 30):
            date = today.shift(days=-i)
            task.append(loop.create_task(self.fetch(date)))
        loop.run_until_complete(asyncio.gather(*task))
        asyncio.run(self.write())


if __name__ == "__main__":
    Downloader().run()
