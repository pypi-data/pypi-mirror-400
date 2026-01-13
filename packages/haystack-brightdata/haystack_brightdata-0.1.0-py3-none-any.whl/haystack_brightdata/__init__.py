"""
Haystack integration for Bright Data web scraping services.

This package provides Haystack components for:
- SERP API: Search engine results from Google, Bing, Yahoo, and more
- Web Unlocker: Access geo-restricted and bot-protected websites
- Web Scraper: Extract structured data from 43+ supported websites

Example usage:
    ```python
    from haystack import Pipeline
    from haystack_brightdata import BrightDataSERP, BrightDataUnlocker, BrightDataWebScraper

    # SERP API - Search engine results
    serp = BrightDataSERP(bright_data_api_key="your-api-key")
    result = serp.run(query="Python tutorials", num_results=20)

    # Web Unlocker - Access restricted content
    unlocker = BrightDataUnlocker(bright_data_api_key="your-api-key")
    result = unlocker.run(url="https://example.com", output_format="markdown")

    # Web Scraper - Extract structured data
    scraper = BrightDataWebScraper(bright_data_api_key="your-api-key")
    result = scraper.run(dataset="amazon_product", url="https://www.amazon.com/dp/...")
    ```
"""

__version__ = "0.1.0"

from .brightdata_scraper import BrightDataWebScraper
from .brightdata_serp import BrightDataSERP
from .brightdata_unlocker import BrightDataUnlocker
from .datasets import get_dataset_info, get_supported_datasets

__all__ = [
    "__version__",
    "BrightDataSERP",
    "BrightDataUnlocker",
    "BrightDataWebScraper",
    "get_supported_datasets",
    "get_dataset_info",
]
