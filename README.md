# Urban Dictionary Scraper

This project is a web scraper designed to scrape and save word definitions from Urban Dictionary's browse pages for all letters ('a' to 'z' and '*'). The scraper uses asynchronous HTTP requests for efficient and fast data collection and includes robust error handling, retry mechanisms, and rate-limiting to avoid overloading the server.

## Features
- **Asynchronous Scraping**: Utilizes `aiohttp` and `asyncio` for non-blocking requests.
- **Retry Logic**: Retries failed requests up to 3 times in case of transient errors.
- **Rate Limiting**: Limits the number of concurrent requests to avoid overwhelming the server.
- **Error Logging**: Logs all failed requests into an error log file (`output/error_log.txt`).
- **JSON Output**: Saves scraped data for each letter in a separate JSON file in the `output` directory.

## Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Create an `output` directory (if not already created by the script):
    ```bash
    mkdir output
    ```

## Usage

Run the script using Python:
```bash
python scraper.py
