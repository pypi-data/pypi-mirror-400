"""Example: Using Bright Data components in Haystack pipelines.

This example demonstrates how to integrate Bright Data components into
Haystack pipelines for data retrieval and processing workflows.
"""

import json
import os
from dotenv import load_dotenv

from haystack import Pipeline, Document
from haystack_brightdata import BrightDataSERP, BrightDataUnlocker, BrightDataWebScraper

# Load environment variables from .env file
load_dotenv()

# Set your Bright Data API key
# Get your API key from: https://brightdata.com/cp/api_access
os.environ["BRIGHT_DATA_API_KEY"] = os.getenv("BRIGHT_DATA_API_KEY", "YOUR_API_KEY_HERE")


# Example 1: Simple SERP Pipeline
print("=" * 80)
print("Example 1: SERP Search Pipeline")
print("=" * 80)

# Create a pipeline with SERP component
serp_pipeline = Pipeline()
serp_pipeline.add_component("search", BrightDataSERP())

# Run the pipeline
print("\nExecuting search for 'Haystack AI framework'...")
result = serp_pipeline.run({
    "search": {
        "query": "Haystack AI framework",
        "num_results": 5,
        "parse_results": True
    }
})

print(f"✓ Search completed!")
print(f"  Results length: {len(result['search']['results'])} characters")
print(f"  Preview: {result['search']['results'][:300]}...")


# Example 2: Web Unlocker Pipeline
print("\n" + "=" * 80)
print("Example 2: Web Unlocker Pipeline")
print("=" * 80)

# Create a pipeline with Unlocker component
unlocker_pipeline = Pipeline()
unlocker_pipeline.add_component("unlocker", BrightDataUnlocker(zone='unblocker'))

# Run the pipeline
print("\nAccessing https://example.com...")
result = unlocker_pipeline.run({
    "unlocker": {
        "url": "https://example.com",
        "output_format": "markdown"
    }
})

print(f"✓ Page accessed!")
print(f"  Content length: {len(result['unlocker']['content'])} characters")
print(f"  Preview: {result['unlocker']['content'][:300]}...")


# Example 3: Web Scraper Pipeline with Data Processing
print("\n" + "=" * 80)
print("Example 3: Web Scraper Pipeline")
print("=" * 80)

# Create a pipeline with Scraper component
scraper_pipeline = Pipeline()
scraper_pipeline.add_component("scraper", BrightDataWebScraper())

# Run the pipeline
print("\nCalling the Bright Data Web Scraper...")
print("Note: This will fail without a valid API key and real URL")

try:
    result = scraper_pipeline.run({
        "scraper": {
            "dataset": "amazon_product",
            "url": "https://www.amazon.com/dp/B08N5WRWNW"  # Example product
        }
    })

    # Parse the JSON data
    data = json.loads(result['scraper']['data'])
    print(f"✓ Data extracted!")
    print(f"  Items: {len(data)}")
    print(f"  Preview: {str(data)[:300]}...")

except Exception as e:
    print(f"✗ Expected error (no valid API key): {str(e)[:200]}...")


# Example 4: Convert Scraper Results to Haystack Documents
print("\n" + "=" * 80)
print("Example 4: Convert to Haystack Documents")
print("=" * 80)


def convert_to_documents(scraper_result: dict) -> list[Document]:
    """Convert Bright Data scraper results to Haystack Documents.

    This function demonstrates how to transform structured data from
    Bright Data into Haystack Document objects for further processing
    in RAG pipelines, indexing, etc.
    """
    documents = []

    try:
        # Parse the JSON data
        data = json.loads(scraper_result)

        for item in data:
            # Example for Amazon products
            if 'title' in item and 'description' in item:
                doc = Document(
                    content=f"{item.get('title', '')}\n\n{item.get('description', '')}",
                    meta={
                        "url": item.get("url", ""),
                        "price": item.get("price", ""),
                        "rating": item.get("rating", ""),
                        "source": "bright_data_amazon"
                    }
                )
                documents.append(doc)

            # Example for social media posts
            elif 'text' in item or 'caption' in item:
                doc = Document(
                    content=item.get('text') or item.get('caption', ''),
                    meta={
                        "url": item.get("url", ""),
                        "author": item.get("author", ""),
                        "likes": item.get("likes", 0),
                        "source": "bright_data_social"
                    }
                )
                documents.append(doc)

            # Generic fallback
            else:
                doc = Document(
                    content=json.dumps(item),
                    meta={"source": "bright_data"}
                )
                documents.append(doc)

    except json.JSONDecodeError:
        # If not JSON, treat as single document
        doc = Document(content=scraper_result, meta={"source": "bright_data"})
        documents.append(doc)

    return documents


# Example usage
print("\nExample: Converting Instagram profile data to Documents...")
sample_data = json.dumps([
    {
        "username": "example_user",
        "bio": "Example bio text",
        "followers": 1000,
        "url": "https://instagram.com/example_user"
    }
])

documents = convert_to_documents(sample_data)
print(f"✓ Converted to {len(documents)} Haystack Document(s)")
for doc in documents:
    print(f"\n  Content: {doc.content[:100]}...")
    print(f"  Meta: {doc.meta}")


# Example 5: Multi-Component Pipeline
print("\n" + "=" * 80)
print("Example 5: Multi-Step Pipeline (SERP → Unlocker)")
print("=" * 80)

# Note: This is a conceptual example. In practice, you'd need custom logic
# to extract URLs from SERP results and pass them to the Unlocker.

print("\nPipeline flow:")
print("1. SERP component searches for a query")
print("2. Extract URLs from search results")
print("3. Unlocker component accesses those URLs")
print("4. Process the content")

print("\nThis would require custom components to:")
print("- Parse SERP results and extract URLs")
print("- Iterate over URLs and call Unlocker")
print("- Aggregate results")


# Example 6: Practical use case - Product Research Pipeline
print("\n" + "=" * 80)
print("Example 6: Product Research Pipeline")
print("=" * 80)

print("\nUse case: Research Amazon products for a category")
print("\nPipeline steps:")
print("1. Use amazon_product_search dataset to find products")
print("2. Extract product URLs from results")
print("3. Use amazon_product dataset to get detailed info for each")
print("4. Use amazon_product_reviews dataset to get reviews")
print("5. Convert to Haystack Documents for RAG/analysis")

# Create the scraper
scraper = BrightDataWebScraper()

print("\nStep 1: Search for products...")
try:
    search_result = scraper.run(
        dataset="amazon_product_search",
        keyword="wireless headphones",
        url="https://www.amazon.com"
    )
    print(f"  ✓ Search completed: {len(search_result['data'])} characters")
except Exception as e:
    print(f"  ✗ Expected error: {str(e)[:100]}...")

print("\nStep 2-5: Extract URLs, get details, reviews, convert to Documents")
print("  (Would require additional processing logic)")


print("\n" + "=" * 80)
print("All Pipeline examples completed!")
print("=" * 80)
print("\nKey Takeaways:")
print("✓ Bright Data components work seamlessly in Haystack pipelines")
print("✓ Results can be easily converted to Haystack Documents")
print("✓ Components can be chained for complex workflows")
print("✓ Perfect for RAG, search, and data extraction pipelines")
