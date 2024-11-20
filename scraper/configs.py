import os

# Configurations
OUTPUT_DIR = "output"
SEMAPHORE_LIMIT = 10  # Maximum concurrent requests
RETRIES = 3  # Number of retries for failed requests
ERROR_LOG_FILE = os.path.join(OUTPUT_DIR, "error_log.txt")
SUMMARY_FILE = os.path.join(OUTPUT_DIR, "summary.json")
