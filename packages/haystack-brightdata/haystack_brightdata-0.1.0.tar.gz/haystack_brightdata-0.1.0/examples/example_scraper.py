"""Example: Using BrightDataWebScraper to extract structured data.

This example demonstrates how to use the Bright Data Web Scraper to extract
structured data from 43+ supported websites including Amazon, LinkedIn,
Instagram, and more.
"""

import json
import os
from dotenv import load_dotenv

from haystack_brightdata import BrightDataWebScraper

# Load environment variables from .env file
load_dotenv()

# Set your Bright Data API key
# Get your API key from: https://brightdata.com/cp/api_access
os.environ["BRIGHT_DATA_API_KEY"] = os.getenv("BRIGHT_DATA_API_KEY", "YOUR_API_KEY_HERE")

# Example 1: List all supported datasets
print("=" * 80)
print("Example 1: List All Supported Datasets")
print("=" * 80)

datasets = BrightDataWebScraper.get_supported_datasets()
print(f"\nTotal supported datasets: {len(datasets)}")
print("\nFirst 10 datasets:")
for i, dataset in enumerate(datasets[:10], 1):
    print(f"{i:2d}. {dataset['id']:30s} - {dataset['description'][:50]}...")

# Example 2: Get dataset information
print("\n" + "=" * 80)
print("Example 2: Get Dataset Information")
print("=" * 80)

dataset_info = BrightDataWebScraper.get_dataset_info("amazon_product")
print(f"\nDataset: {dataset_info['id']}")
print(f"Description: {dataset_info['description']}")
print(f"Required inputs: {dataset_info['inputs']}")

# Example 3: Amazon product scraping
print("\n" + "=" * 80)
print("Example 3: Amazon Product Data Extraction")
print("=" * 80)

scraper = BrightDataWebScraper()

# Note: Replace with a real Amazon product URL
amazon_url = "https://www.amazon.com/dp/B08N5WRWNW"  # Example: Echo Dot

try:
    result = scraper.run(
        dataset="amazon_product",
        url=amazon_url
    )

    # Parse the JSON data
    data = json.loads(result['data'])
    print(f"\n✓ Amazon product data extracted!")
    print(f"  Data items: {len(data)}")
    print(f"  First item preview: {str(data[0] if data else {})[:200]}...")
except Exception as e:
    print(f"\n✗ Error (expected without valid API key or URL): {e}")

# Example 4: Instagram profile scraping
print("\n" + "=" * 80)
print("Example 4: Instagram Profile Data Extraction")
print("=" * 80)

# Note: Replace with a real Instagram profile URL
instagram_url = "https://www.instagram.com/instagram/"  # Official Instagram account

try:
    result = scraper.run(
        dataset="instagram_profiles",
        url=instagram_url
    )

    data = json.loads(result['data'])
    print(f"\n✓ Instagram profile data extracted!")
    print(f"  Data items: {len(data)}")
    print(f"  Preview: {str(data)[:300]}...")
except Exception as e:
    print(f"\n✗ Error (expected without valid API key): {e}")

# Example 5: LinkedIn person profile
print("\n" + "=" * 80)
print("Example 5: LinkedIn Person Profile Data Extraction")
print("=" * 80)

# Note: Replace with a real LinkedIn profile URL
linkedin_url = "https://www.linkedin.com/in/williamhgates/"  # Bill Gates

try:
    result = scraper.run(
        dataset="linkedin_person_profile",
        url=linkedin_url
    )

    data = json.loads(result['data'])
    print(f"\n✓ LinkedIn profile data extracted!")
    print(f"  Data items: {len(data)}")
    print(f"  Preview: {str(data)[:300]}...")
except Exception as e:
    print(f"\n✗ Error (expected without valid API key): {e}")

# Example 6: Google Maps reviews
print("\n" + "=" * 80)
print("Example 6: Google Maps Reviews Extraction")
print("=" * 80)

# Note: Replace with a real Google Maps URL
gmaps_url = "https://www.google.com/maps/place/Statue+of+Liberty"

try:
    result = scraper.run(
        dataset="google_maps_reviews",
        url=gmaps_url,
        days_limit="7"  # Last 7 days of reviews
    )

    data = json.loads(result['data'])
    print(f"\n✓ Google Maps reviews extracted!")
    print(f"  Reviews count: {len(data)}")
    print(f"  Preview: {str(data)[:300]}...")
except Exception as e:
    print(f"\n✗ Error (expected without valid API key): {e}")

# Example 7: YouTube video data
print("\n" + "=" * 80)
print("Example 7: YouTube Video Data Extraction")
print("=" * 80)

# Note: Replace with a real YouTube video URL
youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

try:
    result = scraper.run(
        dataset="youtube_videos",
        url=youtube_url
    )

    data = json.loads(result['data'])
    print(f"\n✓ YouTube video data extracted!")
    print(f"  Data items: {len(data)}")
    print(f"  Preview: {str(data)[:300]}...")
except Exception as e:
    print(f"\n✗ Error (expected without valid API key): {e}")

# Example 8: List datasets by category
print("\n" + "=" * 80)
print("Example 8: Datasets by Category")
print("=" * 80)

from haystack_brightdata.datasets import get_dataset_categories

categories = get_dataset_categories()
for category, dataset_list in categories.items():
    print(f"\n{category} ({len(dataset_list)} datasets):")
    for dataset_id in dataset_list[:3]:  # Show first 3
        print(f"  - {dataset_id}")
    if len(dataset_list) > 3:
        print(f"  ... and {len(dataset_list) - 3} more")

print("\n" + "=" * 80)
print("All Scraper examples completed!")
print("=" * 80)
print("\nNote: To actually run these examples with real data, you need:")
print("1. A valid Bright Data API key (set BRIGHT_DATA_API_KEY environment variable)")
print("2. Valid URLs for the websites you want to scrape")
print("3. Appropriate Bright Data subscription/credits")
