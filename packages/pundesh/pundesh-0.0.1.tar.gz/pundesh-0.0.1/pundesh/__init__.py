"""
GMaps Scraper - Google Maps Business Data Extractor

A powerful, easy-to-use Google Maps scraper that works in Google Colab and locally.

Quick Start (Google Colab):
    # Install
    !pip install gmaps-scraper
    !playwright install chromium
    
    # Use
    from gmaps_scraper import scrape_maps
    df = await scrape_maps("restaurants in New York", max_results=50)

Quick Start (Local):
    from gmaps_scraper import scrape_maps
    import asyncio
    df = asyncio.run(scrape_maps("hotels in London", max_results=30))
"""

from .pundesh import (
    # Main functions
    scrape_maps,
    scrape_maps_sync,
    
    # Classes
    GoogleMapsScraper,
    ScraperConfig,
    Business,
    BusinessList,
    ProxyManager,
    
    # Utilities
    install_browser,
    setup_colab,
    is_colab,
    
    # CLI
    cli_main,
)

__version__ = "0.0.1"
__author__ = "pundachi mwon"
__all__ = [
    "scrape_maps",
    "scrape_maps_sync",
    "GoogleMapsScraper",
    "ScraperConfig",
    "Business",
    "BusinessList",
    "ProxyManager",
    "install_browser",
    "setup_colab",
    "is_colab",
    "cli_main",
]
