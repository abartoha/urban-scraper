import os
import json
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
    
    # Add a random sleep between 2 to 4 seconds
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
    
    # Add a random sleep between 2 to 4 seconds
    delay = random.uniform(2, 4)
    time.sleep(delay)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract the word and word links or any other content you need
            mother_section = soup.select('section.flex-1 div.bg-white.dark\:bg-yankees.p-5.mb-5.rounded-md')[0]
            words = [{a.text: a['href']} for a in mother_section.find_all('a')]
            return char, page_num, words
        return char, page_num, None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return char, page_num, None

def save_to_json(data, letter):
    """Save data to a JSON file for a given letter."""
    if not os.path.exists("output"):
        os.makedirs("output")
    file_path = os.path.join("output", f"{letter.upper()}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

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
                results[page_num] = definitions

    # Save results to a JSON file
    save_to_json(results, char)
    return results

def scrape_all_letters():
    """Scrape all pages for all letters based on the last page number for each letter."""
    characters = [chr(i) for i in range(ord('a'), ord('z') + 1)] + ['*']

    # Get the last page for each character first
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_last_page_link, char): char for char in characters}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching last page numbers"):
            char, last_page_number = future.result()
            if last_page_number:
                # Scrape all pages for this letter if a valid last page is found
                print(f"Scraping all pages for {char.upper()}...")
                scrape_all_pages_for_letter(char, last_page_number)

# Run the scraper and save results
if __name__ == "__main__":
    scrape_all_letters()
