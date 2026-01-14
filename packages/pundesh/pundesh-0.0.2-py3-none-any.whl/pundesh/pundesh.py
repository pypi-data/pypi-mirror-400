"""
GMaps Scraper - Main Module
Google Maps Business Data Extractor

Works in Google Colab and locally.
"""

import datetime
import random
import asyncio
import re
import os
import sys
import subprocess
import shutil
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any, Union

# Third-party imports
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    pd = None
    PANDAS_AVAILABLE = False

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from playwright_stealth import stealth_async
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False


# ============================================================
# ENVIRONMENT DETECTION
# ============================================================

def is_colab() -> bool:
    """Check if running in Google Colab"""
    try:
        import google.colab
        return True
    except ImportError:
        return False


def is_jupyter() -> bool:
    """Check if running in Jupyter notebook"""
    try:
        from IPython import get_ipython
        shell = get_ipython().__class__.__name__
        return shell in ['ZMQInteractiveShell', 'TerminalInteractiveShell']
    except:
        return False


# ============================================================
# COLAB SETUP - CRITICAL FOR COLAB
# ============================================================

async def setup_colab(verbose: bool = True) -> bool:
    """
    Setup everything needed for Google Colab.
    
    This installs system dependencies required by Playwright/Chromium.
    RUN THIS FIRST before scraping in Colab!
    
    Usage:
        from gmaps_scraper import setup_colab, scrape_maps
        
        # Setup first (only once per session)
        await setup_colab()
        
        # Then scrape
        df = await scrape_maps("restaurants in NYC", max_results=50)
    
    Returns:
        bool: True if setup successful
    """
    if verbose:
        print("🚀 Setting up environment...")
        print(f"   Environment: {'Google Colab' if is_colab() else 'Local/Jupyter'}")
    
    success = True
    
    # Step 1: Install system dependencies (required for Chromium)
    if verbose:
        print("\n📦 Step 1/3: Installing system dependencies...")
    
    deps_result = await install_playwright_deps(verbose=verbose)
    if not deps_result:
        success = False
    
    # Step 2: Install Playwright browsers
    if verbose:
        print("\n📦 Step 2/3: Installing Chromium browser...")
    
    browser_result = await _install_browser(verbose=verbose)
    if not browser_result:
        success = False
    
    # Step 3: Verify installation
    if verbose:
        print("\n✅ Step 3/3: Verifying installation...")
    
    verify_result = await _verify_installation(verbose=verbose)
    if not verify_result:
        success = False
    
    if success:
        if verbose:
            print("\n" + "="*50)
            print("✅ Setup complete! You can now use scrape_maps()")
            print("="*50 + "\n")
    else:
        if verbose:
            print("\n" + "="*50)
            print("⚠️ Setup completed with warnings. Try running anyway.")
            print("="*50 + "\n")
    
    return success


async def install_playwright_deps(verbose: bool = True) -> bool:
    """
    Install system dependencies required by Playwright/Chromium
    
    This is the KEY fix for the 'libatk-1.0.so.0' error!
    """
    try:
        # List of required system packages for Chromium
        packages = [
            "libnss3",
            "libnspr4",
            "libatk1.0-0",
            "libatk-bridge2.0-0",
            "libcups2",
            "libdrm2",
            "libxkbcommon0",
            "libxcomposite1",
            "libxdamage1",
            "libxfixes3",
            "libxrandr2",
            "libgbm1",
            "libasound2",
            "libpango-1.0-0",
            "libpangocairo-1.0-0",
            "libcairo2",
            "libatspi2.0-0",
        ]
        
        if is_colab():
            # In Colab, use os.system for apt commands
            if verbose:
                print("   Updating package list...")
            
            os.system("apt-get update -qq > /dev/null 2>&1")
            
            if verbose:
                print(f"   Installing {len(packages)} required packages...")
            
            # Install all packages
            packages_str = " ".join(packages)
            result = os.system(f"apt-get install -qq -y {packages_str} > /dev/null 2>&1")
            
            if result == 0:
                if verbose:
                    print("   ✅ System dependencies installed!")
                return True
            else:
                # Try installing packages one by one
                if verbose:
                    print("   Retrying individual package installation...")
                
                for pkg in packages:
                    os.system(f"apt-get install -qq -y {pkg} > /dev/null 2>&1")
                
                if verbose:
                    print("   ✅ System dependencies installed!")
                return True
        else:
            # Not in Colab - try playwright install-deps
            if verbose:
                print("   Running playwright install-deps...")
            
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install-deps", "chromium"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                if verbose:
                    print("   ✅ Dependencies installed!")
                return True
            else:
                if verbose:
                    print(f"   ⚠️ May need sudo: {result.stderr[:100] if result.stderr else 'Unknown error'}")
                return True  # Continue anyway
                
    except Exception as e:
        if verbose:
            print(f"   ⚠️ Warning: {str(e)[:50]}")
        return False


async def _install_browser(verbose: bool = True) -> bool:
    """Install Chromium browser"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            if verbose:
                print("   ✅ Chromium browser installed!")
            return True
        else:
            if verbose:
                print(f"   ⚠️ Warning: {result.stderr[:100] if result.stderr else 'Check installation'}")
            return False
            
    except Exception as e:
        if verbose:
            print(f"   ❌ Error: {str(e)[:50]}")
        return False


async def _verify_installation(verbose: bool = True) -> bool:
    """Verify Playwright installation works"""
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            await browser.close()
        
        if verbose:
            print("   ✅ Browser launch test passed!")
        return True
        
    except Exception as e:
        if verbose:
            print(f"   ⚠️ Verification warning: {str(e)[:50]}")
        return False


# ============================================================
# CONFIGURATION
# ============================================================

@dataclass
class ScraperConfig:
    """Configuration for the Google Maps scraper"""
    headless: bool = True
    slow_mo: int = 0
    use_proxy: bool = False
    use_stealth: bool = True
    random_delays: bool = True
    min_delay: float = 1.0
    max_delay: float = 3.0
    timeout: int = 60000
    output_folder: str = "GMaps_Data"


# ============================================================
# PROXY MANAGER
# ============================================================

class ProxyManager:
    """Manages proxy rotation for the scraper"""
    
    def __init__(self, proxies: List[Dict[str, str]] = None):
        self.proxies = proxies or []
        self.current_index = 0
        self.failed_proxies = set()
    
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        if not self.proxies:
            return None
        
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self.current_index]
            proxy_key = proxy["server"]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            
            if proxy_key not in self.failed_proxies:
                return proxy
            attempts += 1
        
        self.failed_proxies.clear()
        return self.proxies[0] if self.proxies else None
    
    def mark_failed(self, proxy: Dict[str, str]):
        if proxy:
            self.failed_proxies.add(proxy["server"])
    
    @property
    def available_count(self) -> int:
        return len(self.proxies) - len(self.failed_proxies)


# ============================================================
# FINGERPRINT MANAGER
# ============================================================

class FingerprintManager:
    """Manages browser fingerprints to avoid detection"""
    
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    ]
    
    VIEWPORTS = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1536, "height": 864},
        {"width": 1280, "height": 800},
    ]
    
    TIMEZONES = [
        "America/New_York",
        "America/Los_Angeles",
        "Europe/London",
        "Asia/Kolkata",
    ]
    
    def generate_fingerprint(self) -> Dict[str, Any]:
        return {
            "viewport": random.choice(self.VIEWPORTS),
            "user_agent": random.choice(self.USER_AGENTS),
            "timezone_id": random.choice(self.TIMEZONES),
            "locale": "en-US",
        }


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class Business:
    """Represents a business from Google Maps"""
    name: str = ""
    address: str = ""
    phone_number: str = ""
    website: str = ""
    rating: str = ""
    reviews_count: str = ""
    
    def to_dict(self) -> Dict[str, str]:
        return asdict(self)
    
    def __str__(self) -> str:
        return f"{self.name} | {self.rating}⭐ ({self.reviews_count} reviews)"


@dataclass
class BusinessList:
    """Collection of Business objects with deduplication"""
    business_list: List[Business] = field(default_factory=list)
    _seen_names: set = field(default_factory=set, init=False, repr=False)

    def add_business(self, business: Business) -> bool:
        if business.name and business.name not in self._seen_names:
            self.business_list.append(business)
            self._seen_names.add(business.name)
            return True
        return False

    def dataframe(self):
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required. Install with: pip install pandas")
        return pd.DataFrame([asdict(b) for b in self.business_list])

    def save_to_csv(
        self,
        filename: str = None,
        folder: str = None,
        include_timestamp: bool = False
    ) -> str:
        if folder is None:
            folder = "GMaps_Data"
        
        os.makedirs(folder, exist_ok=True)
        
        if filename is None:
            filename = f"gmaps_results_{len(self.business_list)}_businesses"
        
        # Clean filename
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = filename[:100]
        
        if include_timestamp:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename}_{timestamp}"
        
        filepath = os.path.join(folder, f"{filename}.csv")
        self.dataframe().to_csv(filepath, index=False, encoding='utf-8-sig')
        
        return filepath

    def to_json(self) -> str:
        import json
        return json.dumps([asdict(b) for b in self.business_list], indent=2)

    def __len__(self) -> int:
        return len(self.business_list)
    
    def __iter__(self):
        return iter(self.business_list)
    
    def __getitem__(self, index):
        return self.business_list[index]


# ============================================================
# MAIN SCRAPER CLASS
# ============================================================

class GoogleMapsScraper:
    """
    Google Maps Scraper - Extracts business data from Google Maps
    
    Works in Google Colab and locally.
    """

    def __init__(
        self,
        config: ScraperConfig = None,
        proxies: List[Dict[str, str]] = None
    ):
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError(
                "Playwright is required. Install with:\n"
                "  pip install playwright\n"
                "  playwright install chromium"
            )
        
        self.config = config or ScraperConfig()
        self.proxy_manager = ProxyManager(proxies)
        self.fingerprint_manager = FingerprintManager()
        
        self.browser = None
        self.context = None
        self.page = None
        self.current_proxy = None
        self.current_fingerprint = None

    async def scrape(
        self,
        search_query: str,
        max_results: int = 25,
        save_csv: bool = True,
        csv_filename: str = None,
        output_folder: str = None,
    ):
        """
        Scrape Google Maps for business data
        
        Args:
            search_query: Search term (e.g., "restaurants in New York")
            max_results: Maximum number of results to scrape
            save_csv: Whether to save results to CSV
            csv_filename: Custom CSV filename (without extension)
            output_folder: Custom output folder
        
        Returns:
            pandas DataFrame with scraped data
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required. Install with: pip install pandas")
        
        search_url = "https://www.google.com/maps/search/" + search_query.replace(" ", "+")
        
        async with async_playwright() as p:
            await self._setup_browser(p)
            
            print(f"\n{'='*60}")
            print(f"🔍 Searching: {search_query}")
            print(f"📊 Target: {max_results} results")
            print(f"{'='*60}\n")
            
            # Navigate to search
            try:
                await self.page.goto(search_url, timeout=self.config.timeout, wait_until='domcontentloaded')
            except Exception as e:
                print(f"⚠️ Navigation warning: {str(e)[:50]}")
                
            await self.page.wait_for_timeout(5000)
            await self._handle_consent()
            await self.page.wait_for_timeout(3000)
            
            # Check for results
            listing_selector = 'div[role="feed"] > div > div > a[href*="/maps/place/"]'
            
            if await self.page.locator(listing_selector).count() == 0:
                listing_selector = 'a[href*="/maps/place/"]'
            
            initial_count = await self.page.locator(listing_selector).count()
            
            if initial_count == 0:
                print("❌ No results found!")
                await self._cleanup()
                return pd.DataFrame()
            
            print(f"📋 Initial listings: {initial_count}")
            
            # Scroll for more results
            await self._scroll_results(max_results, listing_selector)
            
            # Get listing URLs
            listing_urls = await self._get_listing_urls(listing_selector, max_results)
            print(f"\n📋 Collected {len(listing_urls)} unique URLs")
            
            # Scrape each listing
            business_list = await self._scrape_by_urls(listing_urls)
            
            df = business_list.dataframe()
            
            # Save CSV
            if save_csv and len(df) > 0:
                if csv_filename is None:
                    csv_filename = search_query.replace(" ", "_").replace(",", "")[:50]
                
                folder = output_folder or self.config.output_folder
                filepath = business_list.save_to_csv(csv_filename, folder)
                print(f"\n📁 Saved: {filepath}")
            
            print(f"\n{'='*60}")
            print(f"🎉 SUCCESS! Scraped {len(business_list)} businesses")
            print(f"{'='*60}\n")
            
            await self._cleanup()
            return df

    async def _get_listing_urls(self, listing_selector: str, max_count: int) -> List[str]:
        """Extract unique URLs from listings"""
        urls = set()
        listings = await self.page.locator(listing_selector).all()
        
        for listing in listings[:max_count]:
            try:
                href = await listing.get_attribute('href')
                if href and '/maps/place/' in href:
                    urls.add(href)
            except:
                continue
        
        return list(urls)

    async def _scrape_by_urls(self, urls: List[str]) -> BusinessList:
        """Scrape each business by URL"""
        business_list = BusinessList()
        total = len(urls)
        
        print(f"\n🔍 Scraping {total} businesses...\n")
        
        for idx, url in enumerate(urls):
            try:
                print(f"[{idx + 1}/{total}] ", end='')
                
                await self.page.goto(url, timeout=30000, wait_until='domcontentloaded')
                await self.page.wait_for_timeout(2000)
                await self._wait_for_detail_panel()
                
                business = await self._extract_business_details()
                
                if business.name:
                    added = business_list.add_business(business)
                    status = "✅" if added else "⏭️ dup"
                    print(f"{status} {business.name[:45]}")
                else:
                    print("⚠️ No name found")
                
                await self._random_delay()
                
            except Exception as e:
                print(f"❌ {str(e)[:40]}")
        
        return business_list

    async def _wait_for_detail_panel(self, timeout: int = 10000):
        """Wait for business detail panel"""
        try:
            await self.page.wait_for_selector('h1.DUwDvf', timeout=timeout)
        except:
            try:
                await self.page.wait_for_selector('h1.fontHeadlineLarge', timeout=5000)
            except:
                pass
        await self.page.wait_for_timeout(500)

    async def _extract_business_details(self) -> Business:
        """Extract business details from current page"""
        business = Business()
        
        # Name
        for selector in ['h1.DUwDvf', 'h1.fontHeadlineLarge', 'div.qBF1Pd.fontHeadlineSmall']:
            try:
                loc = self.page.locator(selector)
                if await loc.count() > 0:
                    business.name = (await loc.first.inner_text()).strip()
                    if business.name:
                        break
            except:
                continue
        
        # Rating
        try:
            rating_loc = self.page.locator('div.F7nice span[aria-hidden="true"]').first
            if await self.page.locator('div.F7nice span[aria-hidden="true"]').count() > 0:
                business.rating = (await rating_loc.inner_text()).strip()
        except:
            pass
        
        # Reviews count
        try:
            reviews_loc = self.page.locator('div.F7nice span[aria-label*="review"]')
            if await reviews_loc.count() > 0:
                text = await reviews_loc.first.get_attribute('aria-label')
                if text:
                    match = re.search(r'([\d,]+)', text)
                    if match:
                        business.reviews_count = match.group(1)
        except:
            pass
        
        # Address
        try:
            addr_loc = self.page.locator('button[data-item-id="address"]')
            if await addr_loc.count() > 0:
                business.address = (await addr_loc.first.inner_text()).strip()
            else:
                addr_loc = self.page.locator('[data-item-id="address"]')
                if await addr_loc.count() > 0:
                    business.address = (await addr_loc.first.inner_text()).strip()
        except:
            pass
        
        # Phone
        try:
            phone_loc = self.page.locator('button[data-item-id*="phone:tel:"]')
            if await phone_loc.count() > 0:
                business.phone_number = (await phone_loc.first.inner_text()).strip()
            else:
                phone_loc = self.page.locator('a[href^="tel:"]')
                if await phone_loc.count() > 0:
                    href = await phone_loc.first.get_attribute('href')
                    if href:
                        business.phone_number = href.replace('tel:', '')
        except:
            pass
        
        # Website
        try:
            web_loc = self.page.locator('a[data-item-id="authority"]')
            if await web_loc.count() > 0:
                business.website = (await web_loc.first.inner_text()).strip()
            else:
                web_loc = self.page.locator('a[data-tooltip="Open website"]')
                if await web_loc.count() > 0:
                    business.website = await web_loc.first.get_attribute('href') or ""
        except:
            pass
        
        return business

    async def _setup_browser(self, playwright):
        """Setup browser with anti-detection measures"""
        print("🚀 Setting up browser...")
        
        self.current_fingerprint = self.fingerprint_manager.generate_fingerprint()
        
        launch_args = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars',
            '--disable-gpu',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-extensions',
        ]
        
        proxy_config = None
        if self.config.use_proxy and self.proxy_manager.available_count > 0:
            self.current_proxy = self.proxy_manager.get_next_proxy()
            if self.current_proxy:
                proxy_config = self.current_proxy
                print(f"🌐 Using proxy: {self.current_proxy['server'][:40]}...")
        
        self.browser = await playwright.chromium.launch(
            headless=self.config.headless,
            slow_mo=self.config.slow_mo,
            args=launch_args
        )
        
        context_options = {
            "viewport": self.current_fingerprint["viewport"],
            "user_agent": self.current_fingerprint["user_agent"],
            "locale": self.current_fingerprint["locale"],
            "timezone_id": self.current_fingerprint["timezone_id"],
        }
        
        if proxy_config:
            context_options["proxy"] = {
                "server": proxy_config["server"],
                "username": proxy_config.get("username", ""),
                "password": proxy_config.get("password", "")
            }
        
        self.context = await self.browser.new_context(**context_options)
        
        if STEALTH_AVAILABLE and self.config.use_stealth:
            await stealth_async(self.context)
            print("🥷 Stealth mode enabled")
        
        self.page = await self.context.new_page()
        
        # Block heavy resources
        await self.page.route(
            "**/*.{png,jpg,jpeg,gif,svg,ico,webp,woff,woff2}",
            lambda route: route.abort()
        )
        
        print("✅ Browser ready")

    async def _random_delay(self):
        if self.config.random_delays:
            delay = random.uniform(self.config.min_delay, self.config.max_delay)
            await self.page.wait_for_timeout(int(delay * 1000))

    async def _handle_consent(self):
        try:
            for btn_text in ['Accept all', 'Accept', 'Reject all', 'I agree']:
                btn = self.page.get_by_role("button", name=btn_text)
                if await btn.count() > 0:
                    await btn.first.click(timeout=5000)
                    print(f"✅ Handled consent: {btn_text}")
                    await self.page.wait_for_timeout(2000)
                    break
        except:
            pass

    async def _scroll_results(self, target_count: int, listing_selector: str):
        """Scroll to load more results"""
        print(f"📜 Scrolling to load {target_count} results...")
        
        scroll_container = None
        for selector in ['div[role="feed"]', 'div.m6QErb[aria-label]']:
            if await self.page.locator(selector).count() > 0:
                scroll_container = self.page.locator(selector).first
                break
        
        previous_count = 0
        stall_count = 0
        
        for _ in range(100):
            if scroll_container:
                await scroll_container.evaluate('(el) => el.scrollBy(0, 1000)')
            else:
                await self.page.mouse.wheel(0, 3000)
            
            await self.page.wait_for_timeout(1500)
            current_count = await self.page.locator(listing_selector).count()
            
            # Progress bar
            progress = min(100, int((current_count / target_count) * 100))
            bar = "█" * (progress // 5) + "░" * (20 - progress // 5)
            print(f"   [{bar}] {current_count}/{target_count}", end='\r')
            
            if current_count >= target_count:
                print(f"\n✅ Reached target: {current_count}")
                break
            
            if current_count == previous_count:
                stall_count += 1
                if stall_count >= 5:
                    print(f"\n⚠️ End of results: {current_count}")
                    break
            else:
                stall_count = 0
            
            previous_count = current_count

    async def _cleanup(self):
        if self.browser:
            await self.browser.close()


# ============================================================
# EASY-TO-USE FUNCTIONS
# ============================================================

async def scrape_maps(
    query: str,
    max_results: int = 25,
    save_csv: bool = True,
    csv_filename: str = None,
    output_folder: str = None,
    headless: bool = True,
    use_proxy: bool = False,
    proxies: List[Dict[str, str]] = None,
    auto_setup: bool = True,
):
    """
    Scrape Google Maps - Easy async function
    
    Args:
        query: Search term (e.g., "restaurants in New York")
        max_results: Maximum results to scrape (default: 25)
        save_csv: Save results to CSV (default: True)
        csv_filename: Custom filename for CSV (default: auto-generated from query)
        output_folder: Folder to save CSV (default: 'GMaps_Data')
        headless: Run browser headless (default: True)
        use_proxy: Enable proxy rotation (default: False)
        proxies: List of proxy configs
        auto_setup: Auto-run setup_colab if in Colab (default: True)
    
    Returns:
        pandas DataFrame with scraped data
    
    Example (Google Colab):
        # First time: run setup
        await setup_colab()
        
        # Then scrape
        df = await scrape_maps("hotels in Paris", max_results=50)
        
    Example (Local):
        import asyncio
        df = asyncio.run(scrape_maps("cafes in London", max_results=30))
    """
    
    config = ScraperConfig(
        headless=headless,
        use_proxy=use_proxy,
        use_stealth=True,
        random_delays=True,
        output_folder=output_folder or "GMaps_Data",
    )
    
    scraper = GoogleMapsScraper(config, proxies=proxies)
    return await scraper.scrape(
        query,
        max_results=max_results,
        save_csv=save_csv,
        csv_filename=csv_filename,
        output_folder=output_folder,
    )


def scrape_maps_sync(
    query: str,
    max_results: int = 25,
    save_csv: bool = True,
    csv_filename: str = None,
    output_folder: str = None,
    headless: bool = True,
    use_proxy: bool = False,
    proxies: List[Dict[str, str]] = None,
):
    """
    Scrape Google Maps - Synchronous version
    
    Use this when you're not in an async context (e.g., regular Python scripts).
    
    Example:
        from gmaps_scraper import scrape_maps_sync
        df = scrape_maps_sync("restaurants in NYC", max_results=50)
    """
    return asyncio.run(scrape_maps(
        query=query,
        max_results=max_results,
        save_csv=save_csv,
        csv_filename=csv_filename,
        output_folder=output_folder,
        headless=headless,
        use_proxy=use_proxy,
        proxies=proxies,
        auto_setup=False,
    ))


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Google Maps Scraper")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-n", "--max-results", type=int, default=25)
    parser.add_argument("-o", "--output", help="Output CSV filename")
    parser.add_argument("--folder", default="GMaps_Data")
    parser.add_argument("--no-save", action="store_true")
    
    args = parser.parse_args()
    
    df = scrape_maps_sync(
        query=args.query,
        max_results=args.max_results,
        save_csv=not args.no_save,
        csv_filename=args.output,
        output_folder=args.folder,
    )
    
    print(f"\nResults: {len(df)} businesses")
