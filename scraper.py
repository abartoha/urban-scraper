import requests
from bs4 import BeautifulSoup

def scrape_links_with_headers():
    base_url = "https://www.urbandictionary.com/browse.php?character="
    characters = [chr(i) for i in range(ord('a'), ord('z') + 1)] + ['*']
    all_links = []

    # Add headers to the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    for char in characters:
        url = f"{base_url}{char}"
        print(f"Scraping: {url}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find all anchor tags with links on the page
            links = [a['href'] for a in soup.find_all('a', href=True)]
            all_links.extend(links)
        else:
            print(f"Failed to scrape {url} (Status code: {response.status_code})")
    
    return all_links

# Run the scraper and print results
links = scrape_links_with_headers()
print(f"Total links scraped: {len(links)}")
print(links)
