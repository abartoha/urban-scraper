import requests
from bs4 import BeautifulSoup

def scrape_links():
    base_url = "https://www.urbandictionary.com/browse.php?character="
    characters = [chr(i) for i in range(ord('a'), ord('z') + 1)] + ['*'] # list of characters
    all_links = []

    for char in characters:
        url = f"{base_url}{char}"
        print(f"Scraping: {url}")
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find all anchor tags with links on the page
            links = [a['href'] for a in soup.find_all('a', href=True)]
            all_links.extend(links)
        else:
            print(f"Failed to scrape {url} (Status code: {response.status_code})")
    
    return all_links

# Run the scraper and print results
links = scrape_links()
print(f"Total links scraped: {len(links)}")
print(links)
