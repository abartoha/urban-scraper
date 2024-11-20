__version__ = "1.0.0"
__author__ = "Al Razi"
__all__ = [
    "config",
    "utils",
    "scraper",
    "retry_handler",
]

# Initialize the output directory on package load
import os
from .config import OUTPUT_DIR

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
