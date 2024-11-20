import requests
from bs4 import BeautifulSoup

def scrape_last_page_links():
    base_url = "https://www.urbandictionary.com/browse.php?character="
    characters = [chr(i) for i in range(ord('a'), ord('z') + 1)] + ['*']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com",
    }

    last_page_links = {}

    for char in characters:
        url = f"{base_url}{char}"
        print(f"Scraping: {url}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            try:
                # Find the <a> tag with aria-label "Last page"
                last_page_tag = soup.find("a", attrs={"aria-label": "Last page"})
                if last_page_tag:
                    last_page_links[char] = last_page_tag['href']
                else:
                    last_page_links[char] = None  # No "Last page" link found
            except Exception as e:
                print(f"Error parsing {url}: {e}")
                last_page_links[char] = None
        else:
            print(f"Failed to scrape {url} (Status code: {response.status_code})")
            last_page_links[char] = None
    
    return last_page_links

# Run the scraper and print results
last_page_hrefs = scrape_last_page_links()
for char, href in last_page_hrefs.items():
    print(f"{char}: {href}")

