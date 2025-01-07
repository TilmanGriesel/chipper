import argparse
import asyncio

from core.webscrape import ScraperConfig, WebScraper


def parse_args():
    parser = argparse.ArgumentParser(description="Web Scraper CLI")
    parser.add_argument(
        "--base-url", default="https://localhost/", help="Base URL to scrape"
    )
    parser.add_argument(
        "--output-dir", default="data", help="Output directory for scraped data"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Number of URLs to process in each batch",
    )
    parser.add_argument(
        "--delay", type=float, default=1.0, help="Delay between batches in seconds"
    )
    return parser.parse_args()


async def run_scrapers(args):
    config = ScraperConfig(
        base_url=args.base_url,
        output_dir=args.output_dir,
        batch_size=args.batch_size,
        delay_between_batches=args.delay,
    )
    scraper = WebScraper(config)
    await scraper.run()


def main():
    args = parse_args()
    asyncio.run(run_scrapers(args))


if __name__ == "__main__":
    main()
