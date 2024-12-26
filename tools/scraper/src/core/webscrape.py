import asyncio
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set
from urllib.parse import urljoin, urlparse

import aiohttp
import trafilatura
from bs4 import BeautifulSoup


@dataclass
class ScraperConfig:
    base_url: str
    output_dir: str = "scraped_content"
    batch_size: int = 10
    delay_between_batches: float = 0.1
    excluded_extensions: Set[str] = None
    max_retries: int = 2
    timeout: int = 15
    max_concurrent_requests: int = 5

    def __post_init__(self):
        if self.excluded_extensions is None:
            self.excluded_extensions = {
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
                ".pdf",
                ".doc",
                ".docx",
                ".zip",
                ".tar",
                ".gz",
                ".mp4",
                ".mp3",
                ".wav",
            }


class WebScraper:
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.base_url = config.base_url
        self.base_domain = urlparse(config.base_url).netloc
        self.output_dir = Path(config.output_dir) / self.base_domain
        self.visited_urls = set()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        self._setup_logging()

    def _setup_logging(self):
        log_file = self.output_dir / f"{self.base_domain}_scraper.log"
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger = logging.getLogger(f"scraper_{self.base_domain}")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)

    def sanitize_filename(self, url: str) -> str:
        filename = url.replace(self.base_url, "").split("?")[0]
        filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
        filename = filename.strip(". ")
        if not filename:
            filename = "index"
        return f"{filename}.txt"

    async def fetch_page(
        self, session: aiohttp.ClientSession, url: str
    ) -> Optional[str]:
        async with self.semaphore:
            for attempt in range(self.config.max_retries):
                try:
                    timeout = aiohttp.ClientTimeout(total=self.config.timeout)
                    async with session.get(url, timeout=timeout) as response:
                        if response.status == 200:
                            return await response.text()
                        self.logger.warning(
                            f"Failed to fetch {url}, status code: {response.status}, "
                            f"attempt {attempt + 1}/{self.config.max_retries}"
                        )
                except Exception as e:
                    self.logger.error(
                        f"Error fetching {url}: {str(e)}, "
                        f"attempt {attempt + 1}/{self.config.max_retries}"
                    )
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(2**attempt)
        return None

    def extract_links(self, html: str, current_url: str) -> List[str]:
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        valid_links = set()
        for link in soup.find_all("a", href=True):
            href = link["href"]
            absolute_url = urljoin(current_url, href)
            parsed_url = urlparse(absolute_url)
            if (
                parsed_url.netloc == self.base_domain
                and absolute_url not in self.visited_urls
                and "#" not in absolute_url
                and "javascript:" not in href
                and not href.startswith("mailto:")
                and not any(
                    href.endswith(ext) for ext in self.config.excluded_extensions
                )
            ):
                cleaned_url = absolute_url.split("#")[0]
                valid_links.add(cleaned_url)
        return list(valid_links)

    async def process_page(self, session: aiohttp.ClientSession, url: str) -> List[str]:
        if url in self.visited_urls:
            return []
        self.visited_urls.add(url)
        self.logger.info(f"Processing {url}")

        html = await self.fetch_page(session, url)
        if not html:
            return []

        content = trafilatura.extract(
            html, include_comments=False, include_tables=True, include_formatting=True
        )

        if content:
            filename = self.sanitize_filename(url)
            output_path = self.output_dir / filename
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(content)
                    f.write(f"\n\nSource URL: {url}\n")
                self.logger.info(f"Saved content to {output_path}")
            except Exception as e:
                self.logger.error(f"Error saving content for {url}: {str(e)}")

        return self.extract_links(html, url)

    async def run(self):
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            urls_to_process = [self.base_url]
            while urls_to_process:
                batch = urls_to_process[: self.config.batch_size]
                urls_to_process = urls_to_process[self.config.batch_size :]
                tasks = [self.process_page(session, url) for url in batch]
                results = await asyncio.gather(*tasks)
                for new_urls in results:
                    urls_to_process.extend(
                        [url for url in new_urls if url not in self.visited_urls]
                    )
                await asyncio.sleep(self.config.delay_between_batches)
        self.logger.info(
            f"Scraping completed. Processed {len(self.visited_urls)} pages."
        )
