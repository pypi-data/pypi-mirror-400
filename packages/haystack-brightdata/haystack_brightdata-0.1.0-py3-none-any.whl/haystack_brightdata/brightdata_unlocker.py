"""Bright Data Web Unlocker component for Haystack.

This component allows you to access geo-restricted and bot-protected websites
using Bright Data's Web Unlocker API.
"""

from typing import Literal, Optional

from haystack import component

from ._utilities import BrightDataUnlockerAPIWrapper


@component
class BrightDataUnlocker:
    """Access geo-restricted and bot-protected websites using Bright Data Web Unlocker.

    This component allows you to bypass anti-bot measures, CAPTCHAs, and geographic
    restrictions when accessing web content. It supports multiple output formats
    including raw HTML, markdown, and screenshots.

    Usage example:
    ```python
    from haystack import Pipeline
    from haystack_brightdata import BrightDataUnlocker

    # Initialize component
    unlocker = BrightDataUnlocker(bright_data_api_key="your-api-key")

    # Use in a pipeline
    pipeline = Pipeline()
    pipeline.add_component("unlocker", unlocker)

    # Run the pipeline
    result = pipeline.run({
        "unlocker": {
            "url": "https://example.com",
            "output_format": "markdown"
        }
    })
    print(result["unlocker"]["content"])
    ```

    Args:
        bright_data_api_key: Bright Data API key. If not provided, will look for
            BRIGHT_DATA_API_KEY environment variable.
        zone: Bright Data zone to use (default: "unlocker")
        default_country: Default country code for geo-targeting (default: "us")
        default_output_format: Default output format - html, markdown, or screenshot
            (default: "html")
    """

    def __init__(
        self,
        bright_data_api_key: Optional[str] = None,
        zone: str = "unlocker",
        default_country: str = "us",
        default_output_format: Literal["html", "markdown", "screenshot"] = "html",
    ):
        """Initialize the BrightDataUnlocker component."""
        # Initialize API wrapper with optional API key
        if bright_data_api_key:
            self.api_wrapper = BrightDataUnlockerAPIWrapper(bright_data_api_key=bright_data_api_key)
        else:
            self.api_wrapper = BrightDataUnlockerAPIWrapper()

        self.zone = zone
        self.default_country = default_country
        self.default_output_format = default_output_format

    @component.output_types(content=str)
    def run(
        self,
        url: str,
        country: Optional[str] = None,
        output_format: Optional[Literal["html", "markdown", "screenshot"]] = None,
        zone: Optional[str] = None,
    ) -> dict:
        """Access a URL and retrieve its content using Bright Data Web Unlocker.

        This method bypasses anti-bot measures, CAPTCHAs, and geographic restrictions
        to access web content that might otherwise be blocked or restricted.

        Args:
            url: URL to access (required)
            country: Two-letter country code for geo-targeting (e.g., "us", "gb", "de")
                This allows you to access content as if you were browsing from that country.
                Defaults to the value set during initialization.
            output_format: Format for the returned content - one of:
                - "html": Raw HTML content (default)
                - "markdown": Content converted to markdown format
                - "screenshot": Base64-encoded screenshot of the page
                Defaults to the value set during initialization.
            zone: Bright Data zone to use. Overrides the default zone set during initialization.

        Returns:
            Dictionary with a single key "content" containing the web page content as a string.
            The format depends on the output_format parameter.

        Raises:
            ValueError: If the API key is invalid or request fails
            requests.HTTPError: If the API returns an error status code

        Example:
            ```python
            unlocker = BrightDataUnlocker()
            result = unlocker.run(
                url="https://example.com/restricted-content",
                country="gb",
                output_format="markdown"
            )
            print(result["content"])
            ```
        """
        # Use provided values or fall back to defaults
        country = country or self.default_country
        output_format = output_format or self.default_output_format
        zone = zone or self.zone

        # Call the API wrapper
        content = self.api_wrapper.get_page_content(
            url=url,
            zone=zone,
            format="raw",
            country=country,
            data_format=output_format,
        )

        return {"content": content}
