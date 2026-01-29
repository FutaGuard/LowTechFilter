from __future__ import annotations

import os
import logging
import re
from abc import ABC, abstractmethod
from html.parser import HTMLParser
from json.decoder import JSONDecodeError
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

IP_PATTERN = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
EXCLUDED_SUFFIXES = ("google.com",)
OUTPUT_FILE = "TW165.txt"
URL_PATTERN = re.compile(
    r'(https?://[^\s<>"\']+ |(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}(?:/[^\s<>"\']*)?)',
    re.IGNORECASE,
)
TRAILING_PUNCT = "。、，,;；:：)）]}]>〉＞"


class BaseContentParser(ABC):
    """Abstract base parser for extracting hostnames from various content sources."""

    @staticmethod
    def normalize_url(raw: str) -> str | None:
        """Normalize a raw URL string and extract the hostname."""
        candidate = raw.strip()
        if not candidate:
            return None
        if candidate.startswith("http//"):
            candidate = "http://" + candidate[6:]
        elif candidate.startswith("https//"):
            candidate = "https://" + candidate[7:]
        if not candidate.startswith(("http://", "https://")):
            candidate = "http://" + candidate
        parsed = urlparse(candidate)
        return parsed.hostname.lower() if parsed.hostname else None

    @abstractmethod
    def extract(self, payload: object) -> list[str]:
        """Extract hostnames from the given payload."""


class NPA165Parser(BaseContentParser):
    """Parser for NPA 165 API responses containing HTML tables with scam URLs."""

    class _TableParser(HTMLParser):
        """Internal HTML table parser for NPA165 content."""

        def __init__(self) -> None:
            super().__init__()
            self._in_table = False
            self._row: list[str] | None = None
            self._cell: list[str] | None = None
            self.rows: list[list[str]] = []

        def handle_starttag(self, tag, attrs):
            if tag == "table":
                self._in_table = True
            elif self._in_table and tag == "tr":
                self._row = []
            elif self._in_table and self._row is not None and tag in {"td", "th"}:
                self._cell = []

        def handle_endtag(self, tag):
            if tag == "table":
                self._in_table = False
                self._row = None
                self._cell = None
            elif self._in_table and tag in {"td", "th"} and self._cell is not None:
                text = "".join(self._cell).replace("\xa0", " ").strip()
                if self._row is not None:
                    self._row.append(text)
                self._cell = None
            elif self._in_table and tag == "tr" and self._row is not None:
                if self._row:
                    self.rows.append(self._row)
                self._row = None

        def handle_data(self, data):
            if self._cell is not None and data:
                self._cell.append(data)

    def extract(self, payload: object) -> list[str]:
        if not isinstance(payload, list):
            logger.warning("Unexpected payload type: %s", type(payload).__name__)
            return []

        hostnames: list[str] = []
        for record in payload:
            content = (record or {}).get("content") or ""
            parser = self._TableParser()
            parser.feed(content)
            parser.close()

            for row in parser.rows:
                for cell in row:
                    for match in URL_PATTERN.findall(cell):
                        cleaned = match.strip().strip(TRAILING_PUNCT)
                        if cleaned:
                            hostname = self.normalize_url(cleaned)
                            if hostname:
                                hostnames.append(hostname)
        return hostnames


class TW165Collector:
    """Collect and deduplicate scam hostnames from TW165 sources."""

    def __init__(self, sources: dict[str, type[BaseContentParser]]):
        self.sources = sources

    @staticmethod
    def _should_skip(hostname: str) -> bool:
        if IP_PATTERN.match(hostname):
            return True
        return any(hostname.endswith(suffix) for suffix in EXCLUDED_SUFFIXES)

    def _fetch(self, url: str) -> object | None:
        try:
            response = requests.get(url, timeout=10)
        except requests.RequestException as exc:
            logger.critical("Fetch error: %s", exc)
            return None

        if response.status_code != 200:
            logger.critical("HTTP %s from %s", response.status_code, url)
            return None

        try:
            return response.json()
        except (JSONDecodeError, ValueError):
            logger.critical("JSON parse error")
            return None

    def collect(self) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []

        for url, parser_cls in self.sources.items():
            payload = self._fetch(url)
            if payload is None:
                continue

            parser = parser_cls()
            for hostname in parser.extract(payload):
                if not hostname or self._should_skip(hostname):
                    continue
                if hostname not in seen:
                    seen.add(hostname)
                    result.append(hostname)
        return result



SOURCES = {
    os.getenv("tw165npa", None): NPA165Parser,
}


def main() -> None:
    existing_hostnames: set[str] = set()
    
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                existing_hostnames = {line.strip() for line in f if line.strip()}
            logger.info("Loaded %d existing hostnames from %s", len(existing_hostnames), OUTPUT_FILE)
        except Exception as exc:
            logger.warning("Failed to read existing file: %s", exc)
    
    collector = TW165Collector(SOURCES)
    new_hostnames = collector.collect()
    
    all_hostnames = existing_hostnames | set(new_hostnames)
    sorted_hostnames = sorted(all_hostnames)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted_hostnames))
    
    logger.info("共有 %d 個網域 (現有: %d, 新增: %d)", 
                len(sorted_hostnames), len(existing_hostnames), len(new_hostnames))


if __name__ == "__main__":
    main()
