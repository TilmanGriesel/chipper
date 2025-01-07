import argparse
import asyncio
import os

from core.webscrape import ScraperConfig, WebScraper

APP_VERSION = os.getenv("APP_VERSION", "[DEV]")


def parse_args():
    parser = argparse.ArgumentParser(
        description=f"Chipper Web Scrape CLI {APP_VERSION}"
    )
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


def show_welcome():
    GREEN = "\033[32m"
    CYAN = "\033[36m"
    RESET = "\033[0m"

    print("\n", flush=True)
    print(f"{GREEN}", flush=True)
    print("        __    _                      ", flush=True)
    print("  _____/ /_  (_)___  ____  ___  _____", flush=True)
    print(" / ___/ __ \\/ / __ \\/ __ \\/ _ \\/ ___/", flush=True)
    print("/ /__/ / / / / /_/ / /_/ /  __/ /    ", flush=True)
    print("\\___/_/ /_/_/ .___/ .___/\\___/_/     ", flush=True)
    print("           /_/   /_/                 ", flush=True)
    print(f"{RESET}", flush=True)
    print(f"{CYAN}       Chipper Scrape {APP_VERSION}", flush=True)
    print(f"{RESET}\n", flush=True)


if __name__ == "__main__":
    show_welcome()
    main()
