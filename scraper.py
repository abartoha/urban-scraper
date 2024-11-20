import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from fake_useragent import UserAgent
import time
import random
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
    delay = random.uniform(2, 4)
    time.sleep(delay)
    
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
                        return char, int(match.group(1))  # Return the page number as integer
        return char, None  # No "Last page" link found
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return char, None

def scrape_page_for_letter(char, page_num):
    """Scrape a single page for a given letter and page number."""
    base_url = "https://www.urbandictionary.com/browse.php?character="
    url = f"{base_url}{char.upper()}&page={page_num}"
    
    # Generate a random User-Agent
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com",
    }
    
    # Add a random sleep between 2 to 10 seconds
    delay = random.uniform(2, 4)
    time.sleep(delay)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract the word and word links or any other content you need
            mother_section = soup.select('section.flex-1 div.bg-white.dark\:bg-yankees.p-5.mb-5.rounded-md')[0]
            words = [{a.text:a['href']} for a in mother_section.find_all('a')]
            # print(words)
            return char, page_num, words
        return char, page_num, None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return char, page_num, None

def scrape_all_pages_for_letter(char, last_page_number):
    """Scrape all pages for a given character from page 1 to the last page."""
    results = {}
    
    # Use ThreadPoolExecutor to scrape all pages concurrently for a given letter
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for page_num in range(1, last_page_number + 1):
            futures.append(executor.submit(scrape_page_for_letter, char, page_num))
        
        # Collect results as they complete
        for future in tqdm(as_completed(futures), total=len(futures), desc=f"Scraping {char.upper()}"):
            char, page_num, definitions = future.result()
            if definitions:
                if char not in results:
                    results[char] = {}
                results[char][page_num] = definitions

    return results

def scrape_all_letters():
    """Scrape all pages for all letters based on the last page number for each letter."""
    characters = [chr(i) for i in range(ord('a'), ord('z') + 1)] + ['*']
    all_results = {}

    # Get the last page for each character first
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_last_page_link, char): char for char in characters}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching last page numbers"):
            char, last_page_number = future.result()
            if last_page_number:
                # Scrape all pages for this letter if a valid last page is found
                print(f"Scraping all pages for {char.upper()}...")
                all_results[char] = scrape_all_pages_for_letter(char, last_page_number)
    
    return all_results

# Run the scraper and print results
if __name__ == "__main__":
    all_letters_results = scrape_all_letters()
    for char, pages in all_letters_results.items():
        for page_num, definitions in pages.items():
            print(f"{char.upper()} - Page {page_num}: {definitions[:3]}...")
