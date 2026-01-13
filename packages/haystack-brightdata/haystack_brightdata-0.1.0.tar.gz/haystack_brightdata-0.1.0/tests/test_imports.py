"""Basic import tests for haystack-brightdata package."""

import pytest


def test_package_import():
    """Test that the package can be imported."""
    import haystack_brightdata

    assert haystack_brightdata.__version__ == "0.1.0"


def test_component_imports():
    """Test that all components can be imported."""
    from haystack_brightdata import (
        BrightDataSERP,
        BrightDataUnlocker,
        BrightDataWebScraper,
    )

    assert BrightDataSERP is not None
    assert BrightDataUnlocker is not None
    assert BrightDataWebScraper is not None


def test_utility_imports():
    """Test that utility functions can be imported."""
    from haystack_brightdata import get_dataset_info, get_supported_datasets

    assert callable(get_supported_datasets)
    assert callable(get_dataset_info)


def test_supported_datasets():
    """Test that get_supported_datasets returns the expected number of datasets."""
    from haystack_brightdata import get_supported_datasets

    datasets = get_supported_datasets()
    assert isinstance(datasets, list)
    assert len(datasets) == 43  # We have 43 datasets


def test_dataset_info():
    """Test that get_dataset_info returns correct information."""
    from haystack_brightdata import get_dataset_info

    info = get_dataset_info("amazon_product")
    assert info["id"] == "amazon_product"
    assert "dataset_id" in info
    assert "description" in info
    assert "inputs" in info


def test_dataset_info_invalid():
    """Test that get_dataset_info raises error for invalid dataset."""
    from haystack_brightdata import get_dataset_info

    with pytest.raises(ValueError, match="not found"):
        get_dataset_info("invalid_dataset_name")
