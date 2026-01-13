"""Utility for Bright Data API interactions."""

import os
import time
from typing import Any, Dict, Literal, Optional

import aiohttp
import requests
from pydantic import BaseModel, ConfigDict, SecretStr, model_validator

BRIGHTDATA_API_URL = "https://api.brightdata.com"


def get_from_dict_or_env(
    data: Dict[str, Any], key: str, env_key: str, default: Optional[str] = None
) -> str:
    """Get a value from a dictionary or environment variable.

    Args:
        data: Dictionary to check for the key
        key: Key to look for in the dictionary
        env_key: Environment variable to check if key not in dictionary
        default: Default value if neither found

    Returns:
        The value from dict, env, or default

    Raises:
        ValueError: If value not found and no default provided
    """
    if key in data and data[key]:
        return data[key]

    env_value = os.environ.get(env_key)
    if env_value:
        return env_value

    if default is not None:
        return default

    raise ValueError(
        f"Did not find {key} in dict or {env_key} in environment variables. "
        f"Please provide the Bright Data API key via the {key} parameter or "
        f"set the {env_key} environment variable."
    )


class BrightDataAPIWrapper(BaseModel):
    """Base wrapper for Bright Data API."""

    bright_data_api_key: SecretStr

    model_config = ConfigDict(
        extra="forbid",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_environment(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that api key exists in environment."""
        bright_data_api_key = get_from_dict_or_env(
            values, "bright_data_api_key", "BRIGHT_DATA_API_KEY"
        )
        values["bright_data_api_key"] = bright_data_api_key
        return values

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.bright_data_api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }


class BrightDataUnlockerAPIWrapper(BrightDataAPIWrapper):
    """Wrapper for Bright Data Web Unlocker API.

    This wrapper can be used with various Bright Data zones, including "Unlocker",
    "scraper", and other API-accessible services.
    """

    def get_page_content(
        self,
        url: str,
        zone: str = "unlocker",
        format: Optional[Literal["raw"]] = "raw",
        country: Optional[str] = None,
        data_format: Optional[Literal["html", "markdown", "screenshot"]] = None,
    ) -> str:
        """Get content from a web page using Bright Data Web Unlocker.

        Args:
            url: URL to access
            zone: Bright Data zone (default "unlocker")
            format: Response format ("raw" is standard)
            country: Two-letter country code for geo-targeting (e.g., "us", "gb")
            data_format: Content format type (html, markdown, screenshot)

        Returns:
            String containing the response data
        """
        params = {"zone": zone, "url": url, "format": format}

        if country:
            params["country"] = country
        if data_format:
            params["data_format"] = data_format

        params = {k: v for k, v in params.items() if v is not None}

        response = requests.post(
            f"{BRIGHTDATA_API_URL}/request",
            json=params,
            headers=self._get_headers(),
        )

        response.raise_for_status()
        return response.text


class BrightDataSERPAPIWrapper(BrightDataAPIWrapper):
    """Wrapper for Bright Data SERP API."""

    def get_search_results(
        self,
        query: str,
        zone: Optional[str] = "serp",
        search_engine: Optional[str] = "google",
        country: Optional[str] = "us",
        language: Optional[str] = "en",
        results_count: Optional[int] = 10,
        search_type: Optional[str] = None,
        device_type: Optional[str] = None,
        parse_results: Optional[bool] = False,
    ) -> str:
        """Get search results using Bright Data SERP API.

        Args:
            query: Search query
            zone: Bright Data zone (default "serp")
            search_engine: Search engine to use (default "google")
            country: Two-letter country code for geo-targeting (e.g., "us", "gb")
            language: Two-letter language code (e.g., "en", "es")
            results_count: Number of results to return
            search_type: Type of search (e.g., "shop", "news", "images")
            device_type: Device type to simulate ("desktop" (Default) or "mobile")
            parse_results: Whether to return parsed JSON results

        Returns:
            String containing the search results
        """
        import urllib.parse

        query_encoded = urllib.parse.quote(query)
        url = f"https://www.{search_engine}.com/search?q={query_encoded}"

        params = []

        if country:
            params.append(f"gl={country}")

        if language:
            params.append(f"hl={language}")

        if results_count:
            params.append(f"num={results_count}")

        if parse_results:
            params.append("brd_json=1")

        if search_type:
            if search_type == "jobs":
                params.append("ibp=htl;jobs")
            else:
                params.append(f"tbm={search_type}")

        if device_type:
            if device_type == "mobile":
                params.append("brd_mobile=1")
            elif device_type == "ios":
                params.append("brd_mobile=ios")
            elif device_type == "android":
                params.append("brd_mobile=android")

        if params:
            url += "&" + "&".join(params)

        request_params = {
            "zone": zone,
            "url": url,
            "format": "raw",
        }

        request_params = {k: v for k, v in request_params.items() if v is not None}

        response = requests.post(
            f"{BRIGHTDATA_API_URL}/request",
            json=request_params,
            headers=self._get_headers(),
        )

        response.raise_for_status()
        return response.text


class BrightDataWebScraperAPIWrapper(BrightDataAPIWrapper):
    """Wrapper for Bright Data Dataset API.

    This wrapper can be used to access Bright Data's structured datasets,
    including product data, social media profiles, and more.
    """

    def get_dataset_data(
        self,
        dataset_id: str,
        url: Optional[str] = None,
        zipcode: Optional[str] = None,
        additional_params: Optional[Dict[str, Any]] = None,
        max_poll_attempts: int = 60,
        poll_interval: int = 1,
    ) -> str:
        """Get structured data from a Bright Data Dataset.

        Args:
            dataset_id: The ID of the Bright Data Dataset to query
            url: URL to extract data from (required for most datasets)
            zipcode: Optional zipcode for location-specific data
            additional_params: Any additional parameters to include in the request
            max_poll_attempts: Maximum number of polling attempts (default: 60)
            poll_interval: Seconds to wait between polls (default: 1)

        Returns:
            String containing the extracted structured data (JSON format)

        Raises:
            ValueError: If the request fails or times out
            requests.HTTPError: If the API returns an error status code
        """
        request_data: Dict[str, Any] = {}

        if url:
            request_data["url"] = url

        if zipcode:
            request_data["zipcode"] = zipcode

        if additional_params:
            filtered_params = {
                k: v for k, v in additional_params.items() if v is not None and v != ""
            }
            request_data.update(filtered_params)

        response = requests.post(
            f"{BRIGHTDATA_API_URL}/datasets/v3/scrape",
            params={"dataset_id": dataset_id, "include_errors": "true"},
            json=[request_data],
            headers=self._get_headers(),
        )

        if response.status_code == 200:
            return response.text

        if response.status_code == 202:
            response_data = response.json()
            snapshot_id = response_data.get("snapshot_id")

            if not snapshot_id:
                raise ValueError(f"No snapshot_id in 202 response: {response.text}")

            for _attempt in range(max_poll_attempts):
                time.sleep(poll_interval)

                snapshot_response = requests.get(
                    f"{BRIGHTDATA_API_URL}/datasets/v3/snapshot/{snapshot_id}",
                    params={"format": "json"},
                    headers=self._get_headers(),
                )

                if snapshot_response.status_code == 200:
                    return snapshot_response.text

                if snapshot_response.status_code == 202:
                    status_data = snapshot_response.json()
                    status = status_data.get("status", "")
                    if status in ["running", "building", "starting"]:
                        continue
                    continue

                raise ValueError(
                    f"Unexpected status {snapshot_response.status_code} while polling: "
                    f"{snapshot_response.text}"
                )

            raise ValueError(
                f"Timeout after {max_poll_attempts * poll_interval} seconds waiting for data"
            )

        error_message = f"Error {response.status_code}: {response.text}"
        raise ValueError(error_message)

    async def get_dataset_data_async(
        self,
        dataset_id: str,
        url: Optional[str] = None,
        zipcode: Optional[str] = None,
        additional_params: Optional[Dict[str, Any]] = None,
        max_poll_attempts: int = 60,
        poll_interval: int = 1,
    ) -> str:
        """Get structured data from a Bright Data Dataset asynchronously.

        Args:
            dataset_id: The ID of the Bright Data Dataset to query
            url: URL to extract data from (required for most datasets)
            zipcode: Optional zipcode for location-specific data
            additional_params: Any additional parameters to include in the request
            max_poll_attempts: Maximum number of polling attempts (default: 60)
            poll_interval: Seconds to wait between polls (default: 1)

        Returns:
            String containing the extracted structured data (JSON format)

        Raises:
            ValueError: If the request fails or times out
            aiohttp.ClientError: If the API returns an error status code
        """
        import asyncio

        request_data: Dict[str, Any] = {}

        if url:
            request_data["url"] = url

        if zipcode:
            request_data["zipcode"] = zipcode

        if additional_params:
            filtered_params = {
                k: v for k, v in additional_params.items() if v is not None and v != ""
            }
            request_data.update(filtered_params)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BRIGHTDATA_API_URL}/datasets/v3/scrape",
                params={"dataset_id": dataset_id, "include_errors": "true"},
                json=[request_data],
                headers=self._get_headers(),
            ) as response:
                if response.status == 200:
                    return await response.text()

                if response.status == 202:
                    response_data = await response.json()
                    snapshot_id = response_data.get("snapshot_id")

                    if not snapshot_id:
                        response_text = await response.text()
                        raise ValueError(f"No snapshot_id in 202 response: {response_text}")

                    for _attempt in range(max_poll_attempts):
                        await asyncio.sleep(poll_interval)

                        async with session.get(
                            f"{BRIGHTDATA_API_URL}/datasets/v3/snapshot/{snapshot_id}",
                            params={"format": "json"},
                            headers=self._get_headers(),
                        ) as snapshot_response:
                            if snapshot_response.status == 200:
                                return await snapshot_response.text()

                            if snapshot_response.status == 202:
                                status_data = await snapshot_response.json()
                                status = status_data.get("status", "")
                                if status in ["running", "building", "starting"]:
                                    continue
                                continue

                            response_text = await snapshot_response.text()
                            raise ValueError(
                                f"Unexpected status {snapshot_response.status} while polling: "
                                f"{response_text}"
                            )

                    raise ValueError(
                        f"Timeout after {max_poll_attempts * poll_interval} seconds waiting for data"
                    )

                response_text = await response.text()
                error_message = f"Error {response.status}: {response_text}"
                raise ValueError(error_message)
