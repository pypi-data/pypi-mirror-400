"""Tests for Haystack components."""

import pytest


class TestBrightDataSERP:
    """Tests for BrightDataSERP component."""

    def test_component_initialization(self):
        """Test that component can be initialized with API key."""
        from haystack_brightdata import BrightDataSERP

        serp = BrightDataSERP(bright_data_api_key="test_key")
        assert serp is not None
        assert serp.zone == "serp"
        assert serp.default_search_engine == "google"

    def test_component_has_run_method(self):
        """Test that component has a run method."""
        from haystack_brightdata import BrightDataSERP

        serp = BrightDataSERP(bright_data_api_key="test_key")
        assert hasattr(serp, "run")
        assert callable(serp.run)


class TestBrightDataUnlocker:
    """Tests for BrightDataUnlocker component."""

    def test_component_initialization(self):
        """Test that component can be initialized with API key."""
        from haystack_brightdata import BrightDataUnlocker

        unlocker = BrightDataUnlocker(bright_data_api_key="test_key")
        assert unlocker is not None
        assert unlocker.zone == "unlocker"
        assert unlocker.default_output_format == "html"

    def test_component_has_run_method(self):
        """Test that component has a run method."""
        from haystack_brightdata import BrightDataUnlocker

        unlocker = BrightDataUnlocker(bright_data_api_key="test_key")
        assert hasattr(unlocker, "run")
        assert callable(unlocker.run)


class TestBrightDataWebScraper:
    """Tests for BrightDataWebScraper component."""

    def test_component_initialization(self):
        """Test that component can be initialized with API key."""
        from haystack_brightdata import BrightDataWebScraper

        scraper = BrightDataWebScraper(bright_data_api_key="test_key")
        assert scraper is not None

    def test_component_has_run_method(self):
        """Test that component has a run method."""
        from haystack_brightdata import BrightDataWebScraper

        scraper = BrightDataWebScraper(bright_data_api_key="test_key")
        assert hasattr(scraper, "run")
        assert callable(scraper.run)

    def test_get_supported_datasets(self):
        """Test static method to get supported datasets."""
        from haystack_brightdata import BrightDataWebScraper

        datasets = BrightDataWebScraper.get_supported_datasets()
        assert isinstance(datasets, list)
        assert len(datasets) == 43

    def test_get_dataset_info(self):
        """Test static method to get dataset info."""
        from haystack_brightdata import BrightDataWebScraper

        info = BrightDataWebScraper.get_dataset_info("amazon_product")
        assert info["id"] == "amazon_product"
        assert "dataset_id" in info
