"""Dataset configurations for Bright Data Web Scraper API.

This module contains metadata for all 45+ supported datasets including:
- E-commerce: Amazon, Walmart, eBay, Home Depot, Zara, Etsy, Best Buy
- LinkedIn: Person profiles, Company profiles, Jobs, Posts, People Search
- Social Media: Instagram, Facebook, TikTok, YouTube, X/Twitter, Reddit
- Business Intelligence: Crunchbase, ZoomInfo
- Search & Commerce: Google Maps, Google Shopping, App Stores, Zillow, Booking.com
- Other: GitHub, Yahoo Finance, Reuters
"""

from typing import Any, Dict, List, Literal

DATASETS: List[Dict[str, Any]] = [
    {
        "id": "amazon_product",
        "dataset_id": "gd_l7q7dkf244hwjntr0",
        "description": "Extract structured Amazon product data. Requires a valid product URL with /dp/ in it.",
        "inputs": ["url"],
    },
    {
        "id": "amazon_product_reviews",
        "dataset_id": "gd_le8e811kzy4ggddlq",
        "description": "Extract structured Amazon product review data. Requires a valid product URL with /dp/ in it.",
        "inputs": ["url"],
    },
    {
        "id": "amazon_product_search",
        "dataset_id": "gd_lwdb4vjm1ehb499uxs",
        "description": "Extract structured Amazon product search data. Requires a valid search keyword and Amazon domain URL.",
        "inputs": ["keyword", "url"],
        "fixed_values": {"pages_to_search": "1"},
    },
    {
        "id": "walmart_product",
        "dataset_id": "gd_l95fol7l1ru6rlo116",
        "description": "Extract structured Walmart product data. Requires a valid product URL with /ip/ in it.",
        "inputs": ["url"],
    },
    {
        "id": "walmart_seller",
        "dataset_id": "gd_m7ke48w81ocyu4hhz0",
        "description": "Extract structured Walmart seller data. Requires a valid Walmart seller URL.",
        "inputs": ["url"],
    },
    {
        "id": "ebay_product",
        "dataset_id": "gd_ltr9mjt81n0zzdk1fb",
        "description": "Extract structured eBay product data. Requires a valid eBay product URL.",
        "inputs": ["url"],
    },
    {
        "id": "homedepot_products",
        "dataset_id": "gd_lmusivh019i7g97q2n",
        "description": "Extract structured Home Depot product data. Requires a valid Home Depot product URL.",
        "inputs": ["url"],
    },
    {
        "id": "zara_products",
        "dataset_id": "gd_lct4vafw1tgx27d4o0",
        "description": "Extract structured Zara product data. Requires a valid Zara product URL.",
        "inputs": ["url"],
    },
    {
        "id": "etsy_products",
        "dataset_id": "gd_ltppk0jdv1jqz25mz",
        "description": "Extract structured Etsy product data. Requires a valid Etsy product URL.",
        "inputs": ["url"],
    },
    {
        "id": "bestbuy_products",
        "dataset_id": "gd_ltre1jqe1jfr7cccf",
        "description": "Extract structured Best Buy product data. Requires a valid Best Buy product URL.",
        "inputs": ["url"],
    },
    {
        "id": "linkedin_person_profile",
        "dataset_id": "gd_l1viktl72bvl7bjuj0",
        "description": "Extract structured LinkedIn person profile data. Requires a valid LinkedIn profile URL.",
        "inputs": ["url"],
    },
    {
        "id": "linkedin_company_profile",
        "dataset_id": "gd_l1vikfnt1wgvvqz95w",
        "description": "Extract structured LinkedIn company profile data. Requires a valid LinkedIn company URL.",
        "inputs": ["url"],
    },
    {
        "id": "linkedin_job_listings",
        "dataset_id": "gd_lpfll7v5hcqtkxl6l",
        "description": "Extract structured LinkedIn job listings data. Requires a valid LinkedIn job URL.",
        "inputs": ["url"],
    },
    {
        "id": "linkedin_posts",
        "dataset_id": "gd_lyy3tktm25m4avu764",
        "description": "Extract structured LinkedIn posts data. Requires a valid LinkedIn post URL.",
        "inputs": ["url"],
    },
    {
        "id": "linkedin_people_search",
        "dataset_id": "gd_m8d03he47z8nwb5xc",
        "description": "Extract structured LinkedIn people search data. Requires URL, first_name, and last_name.",
        "inputs": ["url", "first_name", "last_name"],
    },
    {
        "id": "crunchbase_company",
        "dataset_id": "gd_l1vijqt9jfj7olije",
        "description": "Extract structured Crunchbase company data. Requires a valid Crunchbase company URL.",
        "inputs": ["url"],
    },
    {
        "id": "zoominfo_company_profile",
        "dataset_id": "gd_m0ci4a4ivx3j5l6nx",
        "description": "Extract structured ZoomInfo company profile data. Requires a valid ZoomInfo company URL.",
        "inputs": ["url"],
    },
    {
        "id": "instagram_profiles",
        "dataset_id": "gd_l1vikfch901nx3by4",
        "description": "Extract structured Instagram profile data. Requires a valid Instagram profile URL.",
        "inputs": ["url"],
    },
    {
        "id": "instagram_posts",
        "dataset_id": "gd_lk5ns7kz21pck8jpis",
        "description": "Extract structured Instagram post data. Requires a valid Instagram post URL.",
        "inputs": ["url"],
    },
    {
        "id": "instagram_reels",
        "dataset_id": "gd_lyclm20il4r5helnj",
        "description": "Extract structured Instagram reel data. Requires a valid Instagram reel URL.",
        "inputs": ["url"],
    },
    {
        "id": "instagram_comments",
        "dataset_id": "gd_ltppn085pokosxh13",
        "description": "Extract structured Instagram comments data. Requires a valid Instagram post URL.",
        "inputs": ["url"],
    },
    {
        "id": "facebook_posts",
        "dataset_id": "gd_lyclm1571iy3mv57zw",
        "description": "Extract structured Facebook post data. Requires a valid Facebook post URL.",
        "inputs": ["url"],
    },
    {
        "id": "facebook_marketplace_listings",
        "dataset_id": "gd_lvt9iwuh6fbcwmx1a",
        "description": "Extract structured Facebook marketplace listing data. Requires a valid Facebook marketplace URL.",
        "inputs": ["url"],
    },
    {
        "id": "facebook_company_reviews",
        "dataset_id": "gd_m0dtqpiu1mbcyc2g86",
        "description": "Extract structured Facebook company reviews. Requires a valid Facebook company URL and num_of_reviews.",
        "inputs": ["url", "num_of_reviews"],
    },
    {
        "id": "facebook_events",
        "dataset_id": "gd_m14sd0to1jz48ppm51",
        "description": "Extract structured Facebook events data. Requires a valid Facebook event URL.",
        "inputs": ["url"],
    },
    {
        "id": "tiktok_profiles",
        "dataset_id": "gd_l1villgoiiidt09ci",
        "description": "Extract structured TikTok profile data. Requires a valid TikTok profile URL.",
        "inputs": ["url"],
    },
    {
        "id": "tiktok_posts",
        "dataset_id": "gd_lu702nij2f790tmv9h",
        "description": "Extract structured TikTok post data. Requires a valid TikTok post URL.",
        "inputs": ["url"],
    },
    {
        "id": "tiktok_shop",
        "dataset_id": "gd_m45m1u911dsa4274pi",
        "description": "Extract structured TikTok shop data. Requires a valid TikTok shop product URL.",
        "inputs": ["url"],
    },
    {
        "id": "tiktok_comments",
        "dataset_id": "gd_lkf2st302ap89utw5k",
        "description": "Extract structured TikTok comments data. Requires a valid TikTok video URL.",
        "inputs": ["url"],
    },
    {
        "id": "google_maps_reviews",
        "dataset_id": "gd_luzfs1dn2oa0teb81",
        "description": "Extract structured Google Maps reviews data. Requires a valid Google Maps URL.",
        "inputs": ["url", "days_limit"],
        "defaults": {"days_limit": "3"},
    },
    {
        "id": "google_shopping",
        "dataset_id": "gd_ltppk50q18kdw67omz",
        "description": "Extract structured Google Shopping data. Requires a valid Google Shopping product URL.",
        "inputs": ["url"],
    },
    {
        "id": "google_play_store",
        "dataset_id": "gd_lsk382l8xei8vzm4u",
        "description": "Extract structured Google Play Store app data. Requires a valid Google Play Store app URL.",
        "inputs": ["url"],
    },
    {
        "id": "apple_app_store",
        "dataset_id": "gd_lsk9ki3u2iishmwrui",
        "description": "Extract structured Apple App Store app data. Requires a valid Apple App Store app URL.",
        "inputs": ["url"],
    },
    {
        "id": "zillow_properties_listing",
        "dataset_id": "gd_lfqkr8wm13ixtbd8f5",
        "description": "Extract structured Zillow properties listing data. Requires a valid Zillow listing URL.",
        "inputs": ["url"],
    },
    {
        "id": "booking_hotel_listings",
        "dataset_id": "gd_m5mbdl081229ln6t4a",
        "description": "Extract structured Booking.com hotel listings data. Requires a valid Booking.com hotel URL.",
        "inputs": ["url"],
    },
    {
        "id": "youtube_profiles",
        "dataset_id": "gd_lk538t2k2p1k3oos71",
        "description": "Extract structured YouTube channel profile data. Requires a valid YouTube channel URL.",
        "inputs": ["url"],
    },
    {
        "id": "youtube_videos",
        "dataset_id": "gd_m5mbdl081229ln6t4a",
        "description": "Extract structured YouTube video data. Requires a valid YouTube video URL.",
        "inputs": ["url"],
    },
    {
        "id": "youtube_comments",
        "dataset_id": "gd_lk9q0ew71spt1mxywf",
        "description": "Extract structured YouTube comments data. Requires a valid YouTube video URL.",
        "inputs": ["url", "num_of_comments"],
        "defaults": {"num_of_comments": "10"},
    },
    {
        "id": "reuter_news",
        "dataset_id": "gd_lyptx9h74wtlvpnfu",
        "description": "Extract structured Reuters news data. Requires a valid Reuters news article URL.",
        "inputs": ["url"],
    },
    {
        "id": "github_repository_file",
        "dataset_id": "gd_lyrexgxc24b3d4imjt",
        "description": "Extract structured GitHub repository file data. Requires a valid GitHub file URL.",
        "inputs": ["url"],
    },
    {
        "id": "yahoo_finance_business",
        "dataset_id": "gd_lmrpz3vxmz972ghd7",
        "description": "Extract structured Yahoo Finance business data. Requires a valid Yahoo Finance business URL.",
        "inputs": ["url"],
    },
    {
        "id": "x_posts",
        "dataset_id": "gd_lwxkxvnf1cynvib9co",
        "description": "Extract structured X (Twitter) post data. Requires a valid X post URL.",
        "inputs": ["url"],
    },
    {
        "id": "reddit_posts",
        "dataset_id": "gd_lvz8ah06191smkebj4",
        "description": "Extract structured Reddit post data. Requires a valid Reddit post URL.",
        "inputs": ["url"],
    },
]

# Dataset mappings for quick lookups
DATASET_MAPPING: Dict[str, str] = {d["id"]: d["dataset_id"] for d in DATASETS}
DATASET_INPUTS: Dict[str, List[str]] = {d["id"]: d["inputs"] for d in DATASETS}
DATASET_DEFAULTS: Dict[str, Dict[str, str]] = {d["id"]: d.get("defaults", {}) for d in DATASETS}
DATASET_FIXED_VALUES: Dict[str, Dict[str, str]] = {
    d["id"]: d.get("fixed_values", {}) for d in DATASETS
}
DATASET_DESCRIPTIONS: Dict[str, str] = {d["id"]: d["description"] for d in DATASETS}

# Type alias for all supported dataset types
DatasetType = Literal[
    "amazon_product",
    "amazon_product_reviews",
    "amazon_product_search",
    "walmart_product",
    "walmart_seller",
    "ebay_product",
    "homedepot_products",
    "zara_products",
    "etsy_products",
    "bestbuy_products",
    "linkedin_person_profile",
    "linkedin_company_profile",
    "linkedin_job_listings",
    "linkedin_posts",
    "linkedin_people_search",
    "crunchbase_company",
    "zoominfo_company_profile",
    "instagram_profiles",
    "instagram_posts",
    "instagram_reels",
    "instagram_comments",
    "facebook_posts",
    "facebook_marketplace_listings",
    "facebook_company_reviews",
    "facebook_events",
    "tiktok_profiles",
    "tiktok_posts",
    "tiktok_shop",
    "tiktok_comments",
    "google_maps_reviews",
    "google_shopping",
    "google_play_store",
    "youtube_profiles",
    "youtube_videos",
    "youtube_comments",
    "apple_app_store",
    "reuter_news",
    "github_repository_file",
    "yahoo_finance_business",
    "x_posts",
    "zillow_properties_listing",
    "booking_hotel_listings",
    "reddit_posts",
]


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
    """
    return DATASETS.copy()


def get_dataset_info(dataset_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific dataset.

    Args:
        dataset_id: The dataset identifier (e.g., "amazon_product")

    Returns:
        Dictionary containing dataset metadata

    Raises:
        ValueError: If dataset_id is not found
    """
    for dataset in DATASETS:
        if dataset["id"] == dataset_id:
            return dataset.copy()

    raise ValueError(
        f"Dataset '{dataset_id}' not found. "
        f"Available datasets: {', '.join(DATASET_MAPPING.keys())}"
    )


def get_dataset_categories() -> Dict[str, List[str]]:
    """Get datasets organized by category.

    Returns:
        Dictionary mapping category names to lists of dataset IDs
    """
    return {
        "E-commerce": [
            "amazon_product",
            "amazon_product_reviews",
            "amazon_product_search",
            "walmart_product",
            "walmart_seller",
            "ebay_product",
            "homedepot_products",
            "zara_products",
            "etsy_products",
            "bestbuy_products",
        ],
        "LinkedIn": [
            "linkedin_person_profile",
            "linkedin_company_profile",
            "linkedin_job_listings",
            "linkedin_posts",
            "linkedin_people_search",
        ],
        "Business Intelligence": [
            "crunchbase_company",
            "zoominfo_company_profile",
        ],
        "Instagram": [
            "instagram_profiles",
            "instagram_posts",
            "instagram_reels",
            "instagram_comments",
        ],
        "Facebook": [
            "facebook_posts",
            "facebook_marketplace_listings",
            "facebook_company_reviews",
            "facebook_events",
        ],
        "TikTok": [
            "tiktok_profiles",
            "tiktok_posts",
            "tiktok_shop",
            "tiktok_comments",
        ],
        "Search & Commerce": [
            "google_maps_reviews",
            "google_shopping",
            "google_play_store",
            "apple_app_store",
            "zillow_properties_listing",
            "booking_hotel_listings",
        ],
        "YouTube": [
            "youtube_profiles",
            "youtube_videos",
            "youtube_comments",
        ],
        "Other": [
            "reuter_news",
            "github_repository_file",
            "yahoo_finance_business",
            "x_posts",
            "reddit_posts",
        ],
    }
