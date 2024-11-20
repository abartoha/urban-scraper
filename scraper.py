import os
import json
import asyncio
import aiohttp
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientError
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random
import re
from tqdm import tqdm


async def fetch_last_page_link(session, char):
    """Asynchronously fetch the 'Last page' link for a given character with retry logic."""
    base_url = "https://www.urbandictionary.com/browse.php?character="
    url = f"{base_url}{char.upper()}"
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com",
    }

    retries = 3
    for attempt in range(retries):
        try:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    pagination_div = soup.find("div", attrs={"aria-label": "Pagination"})
                    if pagination_div:
                        last_page_tag = pagination_div.find_all("a")[-1]
                        if last_page_tag and last_page_tag.get("href"):
                            href = last_page_tag["href"]
                            match = re.search(r"page=(\d+)", href)
                            if match:
                                return char, int(match.group(1))
                return char, None
        except (ClientError, asyncio.TimeoutError) as e:
            print(f"Error fetching {url} on attempt {attempt + 1}: {e}")
            await asyncio.sleep(2)
    return char, None


async def scrape_page_for_letter(session, char, page_num):
    """Asynchronously scrape a single page for a given letter and page number with retry logic."""
    base_url = "https://www.urbandictionary.com/browse.php?character="
    url = f"{base_url}{char.upper()}&page={page_num}"
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com",
    }

    retries = 3
    for attempt in range(retries):
        try:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    mother_section = soup.select(
                        "section.flex-1 div.bg-white.dark\:bg-yankees.p-5.mb-5.rounded-md"
                    )[0]
                    words = [{a.text: a["href"]} for a in mother_section.find_all("a")]
                    return char, page_num, words
                return char, page_num, None
        except (ClientError, asyncio.TimeoutError) as e:
            print(f"Error fetching {url} on attempt {attempt + 1}: {e}")
            await asyncio.sleep(2)
    return char, page_num, None


def save_to_json(data, letter):
    """Save data to a JSON file for a given letter."""
    if not os.path.exists("output"):
        os.makedirs("output")
    file_path = os.path.join("output", f"{letter.upper()}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


async def scrape_all_pages_for_letter(session, char, last_page_number):
    """Scrape all pages for a given character from page 1 to the last page."""
    results = {}

    tasks = [
        scrape_page_for_letter(session, char, page_num)
        for page_num in range(1, last_page_number + 1)
    ]

    # Execute scraping tasks concurrently
    for future in tqdm(
        asyncio.as_completed(tasks), total=len(tasks), desc=f"Scraping {char.upper()}"
    ):
        char, page_num, definitions = await future
        if definitions:
            results[page_num] = definitions

    # Save results to a JSON file
    save_to_json(results, char)
    return results


async def scrape_all_letters():
    """Scrape all pages for all letters based on the last page number for each letter."""
    characters = [chr(i) for i in range(ord("a"), ord("z") + 1)] + ["*"]
    results = {}

    async with ClientSession() as session:
        # Step 1: Get last page numbers for all letters
        tasks = [fetch_last_page_link(session, char) for char in characters]
        last_pages = {}
        for future in tqdm(
            asyncio.as_completed(tasks), total=len(tasks), desc="Fetching last pages"
        ):
            char, last_page_number = await future
            if last_page_number:
                last_pages[char] = last_page_number

        # Step 2: Scrape all pages for each letter
        for char, last_page in last_pages.items():
            print(f"Scraping all pages for {char.upper()}...")
            results[char] = await scrape_all_pages_for_letter(session, char, last_page)

    return results


if __name__ == "__main__":
    asyncio.run(scrape_all_letters())
