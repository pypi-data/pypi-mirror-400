"""Bright Data SERP API component for Haystack.

This component allows you to execute search engine queries using Bright Data's SERP API
and integrate the results into Haystack pipelines.
"""

from typing import Optional

from haystack import component

from ._utilities import BrightDataSERPAPIWrapper


@component
class BrightDataSERP:
    """Execute search engine queries using Bright Data SERP API.

    This component allows you to perform search queries across multiple search engines
    (Google, Bing, Yahoo, etc.) with geo-targeting, language customization, and various
    search types (web, images, news, shopping, jobs).

    Usage example:
    ```python
    from haystack import Pipeline
    from haystack_brightdata import BrightDataSERP

    # Initialize component
    serp = BrightDataSERP(bright_data_api_key="your-api-key")

    # Use in a pipeline
    pipeline = Pipeline()
    pipeline.add_component("search", serp)

    # Run the pipeline
    result = pipeline.run({
        "search": {
            "query": "Python tutorials",
            "num_results": 20
        }
    })
    print(result["search"]["results"])
    ```

    Args:
        bright_data_api_key: Bright Data API key. If not provided, will look for
            BRIGHT_DATA_API_KEY environment variable.
        zone: Bright Data zone to use (default: "serp")
        default_search_engine: Default search engine (default: "google")
        default_country: Default country code for geo-targeting (default: "us")
        default_language: Default language code (default: "en")
        default_num_results: Default number of results to return (default: 10)
    """

    def __init__(
        self,
        bright_data_api_key: Optional[str] = None,
        zone: str = "serp",
        default_search_engine: str = "google",
        default_country: str = "us",
        default_language: str = "en",
        default_num_results: int = 10,
    ):
        """Initialize the BrightDataSERP component."""
        # Initialize API wrapper with optional API key
        if bright_data_api_key:
            self.api_wrapper = BrightDataSERPAPIWrapper(bright_data_api_key=bright_data_api_key)
        else:
            self.api_wrapper = BrightDataSERPAPIWrapper()

        self.zone = zone
        self.default_search_engine = default_search_engine
        self.default_country = default_country
        self.default_language = default_language
        self.default_num_results = default_num_results

    @component.output_types(results=str)
    def run(
        self,
        query: str,
        search_engine: Optional[str] = None,
        country: Optional[str] = None,
        language: Optional[str] = None,
        num_results: Optional[int] = None,
        search_type: Optional[str] = None,
        device_type: Optional[str] = None,
        parse_results: Optional[bool] = True,
        zone: Optional[str] = None,
    ) -> dict:
        """Execute a search query using Bright Data SERP API.

        Args:
            query: Search query string (required)
            search_engine: Search engine to use (google, bing, yahoo, etc.)
                Defaults to the value set during initialization.
            country: Two-letter country code for geo-targeting (e.g., "us", "gb", "de")
                Defaults to the value set during initialization.
            language: Two-letter language code (e.g., "en", "es", "fr")
                Defaults to the value set during initialization.
            num_results: Number of results to return (max: 100)
                Defaults to the value set during initialization.
            search_type: Type of search - one of: web, images, news, shopping, jobs
                If not specified, performs a standard web search.
            device_type: Device type to simulate - one of: desktop, mobile, ios, android
                If not specified, uses desktop.
            parse_results: Whether to return parsed JSON results instead of raw HTML
                (default: True)
            zone: Bright Data zone to use. Overrides the default zone set during initialization.

        Returns:
            Dictionary with a single key "results" containing the search results as a string.
            If parse_results is True, returns JSON-formatted results.
            Otherwise, returns raw HTML from the search engine.

        Raises:
            ValueError: If the API key is invalid or request fails
            requests.HTTPError: If the API returns an error status code

        Example:
            ```python
            serp = BrightDataSERP()
            result = serp.run(
                query="machine learning tutorials",
                country="us",
                num_results=20,
                search_type="web"
            )
            print(result["results"])
            ```
        """
        # Use provided values or fall back to defaults
        search_engine = search_engine or self.default_search_engine
        country = country or self.default_country
        language = language or self.default_language
        num_results = num_results or self.default_num_results
        zone = zone or self.zone

        # Call the API wrapper
        results = self.api_wrapper.get_search_results(
            query=query,
            zone=zone,
            search_engine=search_engine,
            country=country,
            language=language,
            results_count=num_results,
            search_type=search_type,
            device_type=device_type,
            parse_results=parse_results,
        )

        return {"results": results}
