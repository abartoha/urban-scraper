import os
from scraper.utils import save_error_log
from scraper.config import ERROR_LOG_FILE


def get_failed_pages():
    """Read failed pages from the error log."""
    if os.path.exists(ERROR_LOG_FILE):
        with open(ERROR_LOG_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f.readlines()]
    return []


def retry_failed_pages():
    """Manually retry scraping for failed pages."""
    failed_pages = get_failed_pages()
    if not failed_pages:
        print("No failed pages to retry.")
        return

    # TODO: Implement retry logic (reuse existing scraping functions)
    # Retry logic can call the same scraping functions to reprocess pages
