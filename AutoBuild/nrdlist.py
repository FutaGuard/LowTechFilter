import asyncio
import csv
import gzip
import logging
import os
import pathlib
from base64 import b64encode
from io import BytesIO, TextIOWrapper
from itertools import chain, islice
from typing import Dict, List, Set
from zipfile import ZipFile, BadZipfile

import arrow
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase1:
    def __init__(self):
        self.base_url = os.getenv("PHASE1_URL", "")
        if not self.base_url:
            raise ValueError("PHASE1_URL not set")
        self.data: Dict[str, List[bytes]] = {}

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
                    ).splitlines()
            except BadZipfile:
                logger.error("Bad Zipfile: %s", url)
                return False
            return True

    async def run(self):
        today = arrow.utcnow()
        for i in range(1, 31, 5):
            task = [
                asyncio.create_task(self.fetch(today.shift(days=-j)))
                for j in range(i, i + 5)
            ]
            await asyncio.gather(*task)


class Phase2:
    def __init__(self):
        self.base_url = os.getenv("PHASE2_URL", "")
        if not self.base_url:
            raise ValueError("PHASE2_URL not set")
        self.data: Dict[str, List[bytes]] = {}

    async def fetch(self):
        now = arrow.utcnow()
        async with httpx.AsyncClient() as client:
            for files in ["nrd-1m.csv", "nrd-1w.csv"]:
                url = self.base_url + files
                logger.info("Downloading: %s", files)
                r = await client.get(url)
                if r.status_code != 200:
                    logger.error("Download failed: %s", files)
                    return False
                if files == "nrd-1m.csv":
                    self.data[now.shift(months=-1).date().strftime("%Y-%m-%d")] = (
                        BytesIO(r.content).getvalue().splitlines()
                    )
                else:
                    self.data[now.shift(weeks=-1).date().strftime("%Y-%m-%d")] = (
                        BytesIO(r.content).getvalue().splitlines()
                    )

    async def run(self):
        await self.fetch()


class Phase3:
    def __init__(self):
        self.base_url = os.getenv("PHASE3_URL", "")
        if not self.base_url:
            raise ValueError("PHASE3_URL not set")
        self.data: Dict[str, List[bytes]] = {}

    async def fetch(self):
        async with httpx.AsyncClient() as client:
            logger.info("Downloading: %s", self.base_url)
            r = await client.get(self.base_url)
            if r.status_code != 200:
                logger.error("Download failed: %s", self.base_url)
                return False

            with gzip.GzipFile(fileobj=BytesIO(r.content), mode="rb") as f:
                data_file = TextIOWrapper(BytesIO(f.read()))

        reader = csv.DictReader(data_file)
        for row in reader:
            if row["create_date"]:
                self.data.setdefault(row["create_date"], []).append(
                    row["domain_name"].encode()
                )

    async def run(self):
        await self.fetch()


class Phase4:
    def __init__(self):
        self.base_url = os.getenv("PHASE4_URL", "")
        if not self.base_url:
            raise ValueError("PHASE4_URL not set")
        self.data: Dict[str, List[bytes]] = {}

    async def fetch(self):
        now = arrow.utcnow()
        async with httpx.AsyncClient() as client:
            logger.info("Downloading: %s", self.base_url)
            r = await client.get(self.base_url)
            if r.status_code != 200:
                logger.error("Download failed: %s", self.base_url)
                return False
            date = now.shift(days=-7).date().strftime("%Y-%m-%d")
            self.data[date] = r.content.splitlines()[2:-1]

    async def run(self):
        for _ in range(5):
            try:
                await self.fetch()
            except httpx.ReadTimeout:
                logger.error("Phase4: Timeout, retrying")
                continue
            finally:
                break


async def write_files(datalist: List[Dict[str, List[bytes]]]):
    base_path = pathlib.Path("nrd")
    if not base_path.exists():
        base_path.mkdir()

    sorted_date = sorted(chain.from_iterable(datalist), reverse=True)
    # combine only the first 30 days
    combined_data: Dict[str, Set[bytes]] = {
        date: set() for date in islice(sorted_date, 30)
    }
    for data in datalist:
        for key, value in data.items():
            if key not in combined_data:
                continue
            combined_data[key].update(value)

    dataset = set()
    # combined_data is ordered by insertion (sorted date)
    for i, data in enumerate(combined_data.values(), start=1):
        dataset.update(data)
        # accumulate = "\n".join(sorted(set(accumulate.split("\n"))))
        base_path.joinpath(f"past-{i:02d}day.txt").write_bytes(
            b"\n".join(dataset)
        )


async def main():
    import time

    start = time.time()
    ph1 = Phase1()
    ph2 = Phase2()
    ph3 = Phase3()
    ph4 = Phase4()

    task = [
        asyncio.create_task(ph1.run()),
        asyncio.create_task(ph2.run()),
        asyncio.create_task(ph3.run()),
        asyncio.create_task(ph4.run()),
    ]
    await asyncio.gather(*task)
    logger.info("Download Complete, Now writing")
    await write_files([ph1.data, ph2.data, ph3.data, ph4.data])
    end = time.time() - start
    logger.info(f"Time taken: {end:.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
