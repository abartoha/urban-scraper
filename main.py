import asyncio
from scraper.scraper import fetch_last_page_link, scrape_all_pages
from scraper.utils import save_summary, save_error_log
from scraper.config import SEMAPHORE_LIMIT
from aiohttp import ClientSession


async def main():
    characters = [chr(i) for i in range(ord("a"), ord("z") + 1)] + ["*"]
    semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)
    summary = {"total_letters": 0, "total_pages": 0, "errors": []}

    async with ClientSession() as session:
        # Fetch last pages
        last_pages = {}
        for char in characters:
            last_page = await fetch_last_page_link(session, char, semaphore)
            if last_page:
                last_pages[char] = last_page

        # Scrape each letter
        for char, last_page in last_pages.items():
            print(f"Scraping {char.upper()}...")
            results = await scrape_all_pages(session, char, last_page, semaphore)
            summary["total_letters"] += 1
            summary["total_pages"] += len(results)

    # Save the summary
    save_summary(summary)


if __name__ == "__main__":
    asyncio.run(main())
