"""Bright Data Web Scraper component for Haystack.

This component allows you to extract structured data from 43+ supported websites
using Bright Data's Dataset API.
"""

from typing import Any, Dict, List, Optional

from haystack import component

from ._utilities import BrightDataWebScraperAPIWrapper
from .datasets import (
    DATASET_DEFAULTS,
    DATASET_DESCRIPTIONS,
    DATASET_FIXED_VALUES,
    DATASET_INPUTS,
    DATASET_MAPPING,
    get_dataset_info,
    get_supported_datasets,
)


@component
class BrightDataWebScraper:
    """Extract structured data from 43+ websites using Bright Data's Dataset API.

    This component supports extracting data from:
    - E-commerce: Amazon, Walmart, eBay, Home Depot, Zara, Etsy, Best Buy
    - LinkedIn: Person profiles, Company profiles, Jobs, Posts, People Search
    - Social Media: Instagram, Facebook, TikTok, YouTube, X/Twitter, Reddit
    - Business Intelligence: Crunchbase, ZoomInfo
    - Search & Commerce: Google Maps, Google Shopping, App Stores, Zillow, Booking.com
    - Other: GitHub, Yahoo Finance, Reuters

    Usage example:
    ```python
    from haystack import Pipeline
    from haystack_brightdata import BrightDataWebScraper

    # Initialize component
    scraper = BrightDataWebScraper(bright_data_api_key="your-api-key")

    # Use in a pipeline
    pipeline = Pipeline()
    pipeline.add_component("scraper", scraper)

    # Run the pipeline
    result = pipeline.run({
        "scraper": {
            "dataset": "amazon_product",
            "url": "https://www.amazon.com/dp/B08N5WRWNW"
        }
    })
    print(result["scraper"]["data"])
    ```

    Args:
        bright_data_api_key: Bright Data API key. If not provided, will look for
            BRIGHT_DATA_API_KEY environment variable.
        default_include_errors: Whether to include errors in the output by default
            (default: False)
    """

    def __init__(
        self,
        bright_data_api_key: Optional[str] = None,
        default_include_errors: bool = False,
    ):
        """Initialize the BrightDataWebScraper component."""
        # Initialize API wrapper with optional API key
        if bright_data_api_key:
            self.api_wrapper = BrightDataWebScraperAPIWrapper(
                bright_data_api_key=bright_data_api_key
            )
        else:
            self.api_wrapper = BrightDataWebScraperAPIWrapper()

        self.default_include_errors = default_include_errors

    @component.output_types(data=str)
    def run(
        self,
        dataset: str,
        url: Optional[str] = None,
        keyword: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        num_of_reviews: Optional[str] = None,
        num_of_comments: Optional[str] = None,
        days_limit: Optional[str] = None,
        zipcode: Optional[str] = None,
        **additional_params: Any,
    ) -> dict:
        """Extract structured data from a supported website.

        Args:
            dataset: Dataset type to use. Must be one of the 43 supported datasets.
                Use get_supported_datasets() to see all available options.
            url: URL to extract data from. Required for most datasets.
            keyword: Search keyword. Required for amazon_product_search.
            first_name: First name. Required for linkedin_people_search.
            last_name: Last name. Required for linkedin_people_search.
            num_of_reviews: Number of reviews to fetch. Required for facebook_company_reviews.
            num_of_comments: Number of comments to fetch. Used by youtube_comments (default: 10).
            days_limit: Number of days to limit results. Used by google_maps_reviews (default: 3).
            zipcode: Zipcode for location-specific data.
            **additional_params: Additional dataset-specific parameters.

        Returns:
            Dictionary with a single key "data" containing the extracted structured data
            as a JSON-formatted string.

        Raises:
            ValueError: If dataset is invalid, required parameters are missing, or request fails
            requests.HTTPError: If the API returns an error status code

        Example:
            ```python
            # Amazon product data
            scraper = BrightDataWebScraper()
            result = scraper.run(
                dataset="amazon_product",
                url="https://www.amazon.com/dp/B08N5WRWNW"
            )

            # LinkedIn people search
            result = scraper.run(
                dataset="linkedin_people_search",
                url="https://www.linkedin.com",
                first_name="John",
                last_name="Doe"
            )

            # Instagram profile
            result = scraper.run(
                dataset="instagram_profiles",
                url="https://www.instagram.com/username/"
            )
            ```
        """
        # Validate dataset type
        if dataset not in DATASET_MAPPING:
            available = ", ".join(sorted(DATASET_MAPPING.keys()))
            raise ValueError(
                f"Invalid dataset type: '{dataset}'. "
                f"Available datasets: {available}\n\n"
                f"Use BrightDataWebScraper.get_supported_datasets() to see all options."
            )

        # Get dataset configuration
        dataset_id = DATASET_MAPPING[dataset]
        required_inputs = DATASET_INPUTS[dataset]
        defaults = DATASET_DEFAULTS[dataset]
        fixed_values = DATASET_FIXED_VALUES[dataset]

        # Build parameter dictionary
        provided_params = {
            "url": url,
            "keyword": keyword,
            "first_name": first_name,
            "last_name": last_name,
            "num_of_reviews": num_of_reviews,
            "num_of_comments": num_of_comments,
            "days_limit": days_limit,
        }

        # Build additional parameters for the API call
        api_params: Dict[str, Any] = {}

        # Process required inputs (excluding 'url' which is handled separately)
        for input_name in required_inputs:
            if input_name == "url":
                continue  # URL is handled separately below

            value = provided_params.get(input_name)
            if value is None:
                # Check if there's a default value
                if input_name in defaults:
                    value = defaults[input_name]
                else:
                    # Required parameter is missing
                    raise ValueError(
                        f"Missing required parameter '{input_name}' for dataset '{dataset}'. "
                        f"Required inputs: {required_inputs}\n\n"
                        f"Description: {DATASET_DESCRIPTIONS[dataset]}"
                    )
            api_params[input_name] = value

        # Add fixed values
        api_params.update(fixed_values)

        # Add any additional parameters
        api_params.update(additional_params)

        # Validate URL if required
        if "url" in required_inputs and not url:
            raise ValueError(
                f"URL is required for dataset type '{dataset}'.\n\n"
                f"Description: {DATASET_DESCRIPTIONS[dataset]}"
            )

        # Call the API wrapper
        try:
            data = self.api_wrapper.get_dataset_data(
                dataset_id=dataset_id,
                url=url or "",
                zipcode=zipcode,
                additional_params=api_params if api_params else None,
            )

            if not data:
                raise ValueError(
                    f"No data returned for dataset '{dataset}'. "
                    f"Please verify the URL and parameters are correct."
                )

            return {"data": data}

        except Exception as e:
            # Re-raise with more context
            raise ValueError(
                f"Error extracting data from dataset '{dataset}': {str(e)}\n\n"
                f"Dataset description: {DATASET_DESCRIPTIONS[dataset]}\n"
                f"Required inputs: {required_inputs}"
            ) from e

    @staticmethod
    def get_supported_datasets() -> List[Dict[str, Any]]:
        """Get a list of all supported datasets with their metadata.

        Returns:
            List of dictionaries containing dataset information including:
            - id: Dataset identifier
            - dataset_id: Bright Data internal dataset ID
            - description: Human-readable description
            - inputs: List of required input parameters
            - defaults: Optional default values for parameters
            - fixed_values: Optional fixed parameter values

        Example:
            ```python
            datasets = BrightDataWebScraper.get_supported_datasets()
            for dataset in datasets:
                print(f"{dataset['id']}: {dataset['description']}")
            ```
        """
        return get_supported_datasets()

    @staticmethod
    def get_dataset_info(dataset_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific dataset.

        Args:
            dataset_id: The dataset identifier (e.g., "amazon_product")

        Returns:
            Dictionary containing dataset metadata

        Raises:
            ValueError: If dataset_id is not found

        Example:
            ```python
            info = BrightDataWebScraper.get_dataset_info("amazon_product")
            print(info["description"])
            print(f"Required inputs: {info['inputs']}")
            ```
        """
        return get_dataset_info(dataset_id)
