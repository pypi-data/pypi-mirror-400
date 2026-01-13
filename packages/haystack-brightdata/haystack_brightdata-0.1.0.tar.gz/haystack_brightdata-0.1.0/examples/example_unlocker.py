"""Example: Using BrightDataUnlocker to access restricted websites.

This example demonstrates how to use the Bright Data Web Unlocker to bypass
anti-bot measures, CAPTCHAs, and geographic restrictions.
"""

import os
from dotenv import load_dotenv

from haystack_brightdata import BrightDataUnlocker

load_dotenv()

# Get your API key from: https://brightdata.com/cp/api_access
os.environ["BRIGHT_DATA_API_KEY"] = os.getenv("BRIGHT_DATA_API_KEY", "YOUR_API_KEY_HERE")

# Example 1: Basic HTML content extraction
print("=" * 80)
print("Example 1: Basic HTML Content Extraction")
print("=" * 80)

unlocker = BrightDataUnlocker(zone='unblocker')
result = unlocker.run(
    url="https://example.com",
    output_format="html"
)

print(f"\nPage accessed! Content length: {len(result['content'])} characters")
print(f"First 500 characters:\n{result['content'][:500]}...")

# Example 2: Markdown format
print("\n" + "=" * 80)
print("Example 2: Convert Content to Markdown")
print("=" * 80)

result = unlocker.run(
    url="https://news.ycombinator.com",
    output_format="markdown"
)

print(f"\nPage converted to markdown! Content length: {len(result['content'])} characters")
print(f"First 800 characters:\n{result['content'][:800]}...")

# Example 3: Geo-targeted access
print("\n" + "=" * 80)
print("Example 3: Geo-targeted Access (UK)")
print("=" * 80)

result = unlocker.run(
    url="https://www.bbc.com",
    country="gb",  # Access from United Kingdom
    output_format="html"
)

print(f"\nPage accessed from UK! Content length: {len(result['content'])} characters")
print(f"First 500 characters:\n{result['content'][:500]}...")

# Example 4: Access with different country
print("\n" + "=" * 80)
print("Example 4: Access from Different Country (Germany)")
print("=" * 80)

result = unlocker.run(
    url="https://www.amazon.de",
    country="de",  # Access from Germany
    output_format="markdown"
)

print(f"\nAmazon.de accessed from Germany! Content length: {len(result['content'])} characters")
print(f"First 500 characters:\n{result['content'][:500]}...")

# Example 5: Multiple pages
print("\n" + "=" * 80)
print("Example 5: Access Multiple Pages")
print("=" * 80)

urls = [
    "https://example.com",
    "https://example.org",
    "https://example.net",
]

for url in urls:
    result = unlocker.run(
        url=url,
        output_format="markdown"
    )
    print(f"\n✓ {url}: {len(result['content'])} characters")
    print(f"  Preview: {result['content'][:100]}...")

print("\n" + "=" * 80)
print("All Unlocker examples completed successfully!")
print("=" * 80)
