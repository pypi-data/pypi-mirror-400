"""Example: Using BrightDataSERP to perform search queries.

This example demonstrates how to use the Bright Data SERP API to execute
search queries and retrieve results from Google, Bing, or other search engines.
"""

import os
from dotenv import load_dotenv

from haystack_brightdata import BrightDataSERP

# Load environment variables from .env file
load_dotenv()

# Set your Bright Data API key
# Get your API key from: https://brightdata.com/cp/api_access
os.environ["BRIGHT_DATA_API_KEY"] = os.getenv("BRIGHT_DATA_API_KEY", "YOUR_API_KEY_HERE")

# Example 1: Basic search query
print("=" * 80)
print("Example 1: Basic Google Search")
print("=" * 80)

serp = BrightDataSERP()
result = serp.run(
    query="Haystack AI framework tutorials",
    num_results=5
)

print(f"\nSearch completed! Results length: {len(result['results'])} characters")
print(f"First 500 characters:\n{result['results'][:500]}...")

# Example 2: Search with geo-targeting and language
print("\n" + "=" * 80)
print("Example 2: Geo-targeted Search (Germany, German language)")
print("=" * 80)

result = serp.run(
    query="machine learning",
    country="de",
    language="de",
    num_results=10
)

print(f"\nSearch completed! Results length: {len(result['results'])} characters")
print(f"First 300 characters:\n{result['results'][:300]}...")

# Example 3: News search
print("\n" + "=" * 80)
print("Example 3: News Search")
print("=" * 80)

result = serp.run(
    query="artificial intelligence",
    search_type="news",
    country="us",
    num_results=5
)

print(f"\nNews search completed! Results length: {len(result['results'])} characters")
print(f"First 300 characters:\n{result['results'][:300]}...")

# Example 4: Parsed JSON results
print("\n" + "=" * 80)
print("Example 4: Parsed JSON Results")
print("=" * 80)

result = serp.run(
    query="Python programming",
    num_results=3,
    parse_results=True  # Returns structured JSON instead of raw HTML
)

print(f"\nParsed search completed! Results length: {len(result['results'])} characters")
print(f"First 500 characters:\n{result['results'][:500]}...")

# Example 5: Image search
print("\n" + "=" * 80)
print("Example 5: Image Search")
print("=" * 80)

result = serp.run(
    query="data visualization",
    search_type="images",
    num_results=10
)

print(f"\nImage search completed! Results length: {len(result['results'])} characters")
print(f"First 300 characters:\n{result['results'][:300]}...")

print("\n" + "=" * 80)
print("All SERP examples completed successfully!")
print("=" * 80)
