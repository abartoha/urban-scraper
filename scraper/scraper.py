import asyncio
import aiohttp
from aiohttp.client_exceptions import ClientError
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from scraper.utils import save_to_json_compressed, load_existing_data
from scraper.config import RETRIES


async def fetch_page(session, url, headers):
    """Fetch a URL with retry logic."""
    for attempt in range(RETRIES):
        try:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
        except (ClientError, asyncio.TimeoutError) as e:
            print(f"Error fetching {url} (Attempt {attempt + 1}): {e}")
            await asyncio.sleep(2)
    return None


async def fetch_last_page_link(session, char, semaphore):
    """Fetch the 'Last page' link for a given character with rate-limiting."""
    base_url = "https://www.urbandictionary.com/browse.php?character="
    url = f"{base_url}{char.upper()}"
    headers = {"User-Agent": UserAgent().random}
    async with semaphore:
        html = await fetch_page(session, url, headers)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            pagination_div = soup.find("div", attrs={"aria-label": "Pagination"})
            if pagination_div:
                last_page_tag = pagination_div.find_all("a")[-1]
                if last_page_tag and last_page_tag.get("href"):
                    href = last_page_tag["href"]
                    return int(href.split("page=")[-1])
    return None


async def scrape_page(session, char, page_num, semaphore):
    """Scrape a single page for a given character."""
    base_url = "https://www.urbandictionary.com/browse.php?character="
    url = f"{base_url}{char.upper()}&page={page_num}"
    headers = {"User-Agent": UserAgent().random}
    async with semaphore:
        html = await fetch_page(session, url, headers)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            mother_section = soup.select(
                "section.flex-1 div.bg-white.dark\:bg-yankees.p-5.mb-5.rounded-md"
            )[0]
            return [{a.text: a["href"]} for a in mother_section.find_all("a")]
    return None


async def scrape_all_pages(session, char, last_page, semaphore):
    """Scrape all pages for a given letter and save data incrementally."""
    results = load_existing_data(char)  # Resume from previous state
    start_page = max(results.keys(), default=0) + 1

    tasks = [
        scrape_page(session, char, page, semaphore) for page in range(start_page, last_page + 1)
    ]

    for task in asyncio.as_completed(tasks):
        page_data = await task
        if page_data:
            results.update(page_data)
            save_to_json_compressed(results, char)  # Incremental save
    return results
