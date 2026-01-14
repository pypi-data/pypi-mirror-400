"""
GMaps Scraper - Google Maps Business Data Extractor

Works in Google Colab and locally.

Quick Start (Google Colab):
    from gmaps_scraper import setup_colab, scrape_maps
    
    # Run setup first (only once per session)
    await setup_colab()
    
    # Then scrape
    df = await scrape_maps("restaurants in New York", max_results=50)
"""

from .pundesh import (
    # Main functions
    scrape_maps,
    scrape_maps_sync,
    
    # Setup functions
    setup_colab,
    install_playwright_deps,
    
    # Classes
    GoogleMapsScraper,
    ScraperConfig,
    Business,
    BusinessList,
    ProxyManager,
    
    # Utilities
    is_colab,
    is_jupyter,
)

__version__ = "1.0.1"
__author__ = "Your Name"
__all__ = [
    "scrape_maps",
    "scrape_maps_sync",
    "setup_colab",
    "install_playwright_deps",
    "GoogleMapsScraper",
    "ScraperConfig",
    "Business",
    "BusinessList",
    "ProxyManager",
    "is_colab",
    "is_jupyter",
]
