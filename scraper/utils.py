import os
import json
import gzip
from scraper.config import OUTPUT_DIR


def save_to_json_compressed(data, letter):
    """Save data to a compressed JSON file (GZIP) for a given letter."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    file_path = os.path.join(OUTPUT_DIR, f"{letter.upper()}.json.gz")
    with gzip.open(file_path, "wt", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_existing_data(letter):
    """Load existing data for a letter if the JSON file exists."""
    file_path = os.path.join(OUTPUT_DIR, f"{letter.upper()}.json.gz")
    if os.path.exists(file_path):
        with gzip.open(file_path, "rt", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_error_log(errors):
    """Save the error log to a file."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    with open(os.path.join(OUTPUT_DIR, "error_log.txt"), "w", encoding="utf-8") as f:
        for error in errors:
            f.write(error + "\n")


def save_summary(summary):
    """Save the summary report to a JSON file."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    with open(os.path.join(OUTPUT_DIR, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=4)
