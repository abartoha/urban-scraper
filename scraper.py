import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from fake_useragent import UserAgent
import re

def fetch_last_page_link(char):
    """Fetch the 'Last page' link for a given character with a random User-Agent and random delay."""
    base_url = "https://www.urbandictionary.com/browse.php?character="
    url = f"{base_url}{char.upper()}"  # Convert character to uppercase
    
    # Generate a random User-Agent
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com",
    }
    
    # Add a random sleep between 2 to 10 seconds
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the div with aria-label="Pagination"
            pagination_div = soup.find("div", attrs={"aria-label": "Pagination"})
            if pagination_div:
                # Find the last <a> tag within this div
                last_page_tag = pagination_div.find_all("a")[-1]
                if last_page_tag and last_page_tag.get("href"):
                    # Extract the page number from the href
                    href = last_page_tag["href"]
                    match = re.search(r'page=(\d+)', href)  # Match the page number in the URL
                    if match:
                        return char, match.group(1)  # Return the page number
        return char, None  # No "Last page" link found
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return char, None

def scrape_last_page_links_multithreaded():
    """Scrape last page links for all characters using multithreading with fake_useragent and random delays."""
    characters = [chr(i) for i in range(ord('a'), ord('z') + 1)] + ['*']
    results = {}

    # Use ThreadPoolExecutor for multithreading
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit tasks to the executor
        future_to_char = {executor.submit(fetch_last_page_link, char): char for char in characters}

        # Use tqdm to show progress
        for future in tqdm(as_completed(future_to_char), total=len(characters), desc="Scraping"):
            char, page_number = future.result()
            results[char] = page_number

    return results

# Run the scraper and print results
if __name__ == "__main__":
    last_page_numbers = scrape_last_page_links_multithreaded()
    for char, page_number in last_page_numbers.items():
        print(f"{char}: {page_number}")
