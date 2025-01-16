import asyncio
import logging
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set, Tuple
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

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
    retry_403_delay: float = 30.0
    max_403_retries: int = 3
    min_delay: float = 0.5
    max_delay: float = 2.0
    batch_size_variance: float = 0.5
    retain_query_params: bool = True

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
        self._403_encountered = False
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        self._setup_logging()

    def _setup_logging(self):
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger = logging.getLogger(f"scraper_{self.base_domain}")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)

    def sanitize_filename(self, url: str) -> str:
        parsed_url = urlparse(url)
        path = parsed_url.path.replace(self.base_url, "")
        if not path or path == "/":
            path = "index"
        path = path.lstrip("/").replace("/", "_")

        if parsed_url.query:
            query_params = parse_qs(parsed_url.query)
            param_parts = []

            for key in sorted(query_params.keys()):
                clean_key = re.sub(r"[^a-zA-Z0-9]+", "_", key).strip("_")
                values = sorted(query_params[key])
                for value in values:
                    clean_value = re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_")
                    if clean_value:
                        param_parts.append(f"{clean_key}_{clean_value}")
                    else:
                        param_parts.append(clean_key)

            if param_parts:
                path = f"{path}__" + "__".join(param_parts)

        while "__" in path:
            path = path.replace("__", "_")

        path = re.sub(r'[<>:"/\\|?*]', "_", path)
        path = path.strip("_. ")

        if not path:
            path = "index"

        return f"{path}.md"

    async def handle_403(self, url: str, attempt: int) -> None:
        if not self._403_encountered:
            self._403_encountered = True
            self.logger.warning("First 403 error encountered, reducing request rate")
            self.semaphore = asyncio.Semaphore(
                max(1, self.config.max_concurrent_requests // 2)
            )

        delay = round(
            self.config.retry_403_delay * (2**attempt) * (0.5 + random.random()), 2
        )
        self.logger.info(
            f"Received 403 for {url}, waiting {delay} seconds before retry"
        )
        await asyncio.sleep(delay)

    async def fetch_page(
        self, session: aiohttp.ClientSession, url: str
    ) -> Tuple[Optional[str], int]:
        async with self.semaphore:
            for attempt in range(self.config.max_retries):
                try:
                    if url.startswith("file://"):
                        path = urlparse(url).path
                        try:
                            with open(path, "r", encoding="utf-8") as f:
                                return f.read(), 200
                        except Exception as e:
                            self.logger.error(
                                f"Error reading local file {path}: {str(e)}"
                            )
                            return None, -1

                    timeout = aiohttp.ClientTimeout(total=self.config.timeout)
                    await asyncio.sleep(
                        random.uniform(self.config.min_delay, self.config.max_delay)
                    )

                    async with session.get(url, timeout=timeout) as response:
                        if response.status == 200:
                            return await response.text(), 200
                        elif response.status == 403:
                            if attempt < self.config.max_403_retries:
                                await self.handle_403(url, attempt)
                                continue
                            else:
                                self.logger.error(f"Max 403 retries exceeded for {url}")
                                return None, 403
                        else:
                            self.logger.warning(
                                f"Failed to fetch {url}, status code: {response.status}, attempt {attempt + 1}/{self.config.max_retries}"
                            )
                except Exception as e:
                    self.logger.error(
                        f"Error fetching {url}: {str(e)}, attempt {attempt + 1}/{self.config.max_retries}"
                    )
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep((2**attempt) * (0.5 + random.random()))
        return None, -1

    def normalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        if parsed.query:
            query_params = parse_qs(parsed.query)
            sorted_params = []
            for key in sorted(query_params.keys()):
                values = sorted(query_params[key])
                for value in values:
                    sorted_params.append((key, value))
            new_query = urlencode(sorted_params)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
        return url

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
                parsed_url.netloc != self.base_domain
                or "javascript:" in href
                or href.startswith("mailto:")
                or any(href.endswith(ext) for ext in self.config.excluded_extensions)
            ):
                continue

            cleaned_url = absolute_url.split("#")[0]
            normalized_url = self.normalize_url(cleaned_url)

            if normalized_url not in self.visited_urls:
                valid_links.add(normalized_url)

        return list(valid_links)

    async def process_page(self, session: aiohttp.ClientSession, url: str) -> List[str]:
        normalized_url = self.normalize_url(url)
        if normalized_url in self.visited_urls:
            return []
        self.visited_urls.add(normalized_url)
        self.logger.info(f"Processing {url}")

        html, status = await self.fetch_page(session, url)
        if not html:
            if status == 403:
                self.logger.warning(f"Skipping {url} due to persistent 403 error")
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
                batch_size = max(
                    1,
                    int(
                        self.config.batch_size
                        * (
                            1
                            + random.uniform(
                                -self.config.batch_size_variance,
                                self.config.batch_size_variance,
                            )
                        )
                    ),
                )
                urls_batch = random.sample(
                    urls_to_process, min(batch_size, len(urls_to_process))
                )
                urls_to_process = [
                    url for url in urls_to_process if url not in urls_batch
                ]

                tasks = [self.process_page(session, url) for url in urls_batch]
                results = await asyncio.gather(*tasks)

                for new_urls in results:
                    random.shuffle(new_urls)
                    urls_to_process.extend(
                        [url for url in new_urls if url not in self.visited_urls]
                    )

                delay = self.config.delay_between_batches * (0.5 + random.random())
                await asyncio.sleep(delay)

        self.logger.info(
            f"Scraping completed. Processed {len(self.visited_urls)} pages."
        )
