import requests
from bs4 import BeautifulSoup, Tag
import logging
import time
import json
from typing import List, Dict, Optional
from datetime import datetime
from urllib.robotparser import RobotFileParser
from dataclasses import dataclass, asdict
import random
from urllib.parse import urljoin
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class Part:
    """Data model for a part"""
    part_number: str
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    manufacturer: Optional[str]
    category: Optional[str]
    compatibility: List[str]
    url: str
    source: str
    timestamp: str

class RateLimiter:
    """Rate limiter to prevent overloading servers"""
    def __init__(self, min_delay: float = 2.0, max_delay: float = 5.0):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0

    def wait(self):
        """Wait appropriate time between requests"""
        if self.last_request_time > 0:
            elapsed = time.time() - self.last_request_time
            delay = random.uniform(self.min_delay, self.max_delay)
            if elapsed < delay:
                time.sleep(delay - elapsed)
        self.last_request_time = time.time()

class PartsCatalogScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'PartsCatalogBot/1.0 (+https://example.com/bot)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        self.results = []
        self.rate_limiter = RateLimiter()
        
        # Initialize robots.txt parsers
        self.partstree_robots = RobotFileParser()
        self.partstree_robots.set_url('https://www.partstree.com/robots.txt')
        try:
            self.partstree_robots.read()
            logging.info("Successfully loaded PartsTree robots.txt")
        except Exception as e:
            logging.error(f"Error loading PartsTree robots.txt: {str(e)}")
            self.partstree_robots = None

        # Initialize Rotary robots.txt parser
        self.rotary_robots = RobotFileParser()
        self.rotary_robots.set_url('https://www.rotarycorp.com/robots.txt')
        try:
            self.rotary_robots.read()
            logging.info("Successfully loaded Rotary robots.txt")
        except Exception as e:
            logging.error(f"Error loading Rotary robots.txt: {str(e)}")
            self.rotary_robots = None

        # Initialize Stens robots.txt parser
        self.stens_robots = RobotFileParser()
        self.stens_robots.set_url('https://www.stens.com/robots.txt')
        try:
            self.stens_robots.read()
            logging.info("Successfully loaded Stens robots.txt")
        except Exception as e:
            logging.error(f"Error loading Stens robots.txt: {str(e)}")
            self.stens_robots = None

    def can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt"""
        if 'partstree.com' in url and self.partstree_robots:
            return self.partstree_robots.can_fetch(self.headers['User-Agent'], url)
        elif 'rotarycorp.com' in url and self.rotary_robots:
            return self.rotary_robots.can_fetch(self.headers['User-Agent'], url)
        elif 'stens.com' in url and self.stens_robots:
            return self.stens_robots.can_fetch(self.headers['User-Agent'], url)
        return True

    def make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with rate limiting and error handling"""
        if not self.can_fetch(url):
            logging.warning(f"URL not allowed by robots.txt: {url}")
            return None

        self.rate_limiter.wait()
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching {url}: {str(e)}")
            return None

    def parse_partstree_part(self, html: str, url: str) -> Optional[Part]:
        """Parse PartsTree.com part detail page"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract part information based on actual PartsTree.com structure
            part_info = soup.select_one('div.part-info')
            if not part_info:
                logging.warning(f"Could not find part info section on page: {url}")
                return None

            # Get part number from the title or part info section
            part_number_elem = (
                part_info.select_one('span.part-number') or 
                soup.select_one('h1.part-number')
            )
            if not part_number_elem:
                logging.warning(f"Could not find part number on page: {url}")
                return None

            # Get other part details
            name_elem = part_info.select_one('h1') or part_info.select_one('div.part-name')
            description_elem = part_info.select_one('div.part-description')
            price_elem = (
                part_info.select_one('span.price') or 
                part_info.select_one('div.price')
            )
            manufacturer_elem = part_info.select_one('div.manufacturer')
            category_elem = part_info.select_one('div.category')
            
            # Get compatibility list if available
            compatibility = []
            compat_list = (
                soup.select_one('div.compatibility') or 
                soup.select_one('ul.fits-models')
            )
            if compat_list and isinstance(compat_list, Tag):
                compatibility = [
                    item.get_text().strip() 
                    for item in compat_list.select('li')
                    if isinstance(item, Tag)
                ]

            # Extract text values safely
            part_number = part_number_elem.get_text().strip() if isinstance(part_number_elem, Tag) else ''
            name = name_elem.get_text().strip() if name_elem and isinstance(name_elem, Tag) else None
            description = description_elem.get_text().strip() if description_elem and isinstance(description_elem, Tag) else None
            price_text = price_elem.get_text().strip() if price_elem and isinstance(price_elem, Tag) else ''
            manufacturer = manufacturer_elem.get_text().strip() if manufacturer_elem and isinstance(manufacturer_elem, Tag) else None
            category = category_elem.get_text().strip() if category_elem and isinstance(category_elem, Tag) else None

            # Parse price safely
            try:
                price = float(price_text.replace('$', '').replace(',', '')) if price_text else None
            except (ValueError, AttributeError):
                price = None
                logging.warning(f"Could not parse price from {price_text} on page: {url}")

            return Part(
                part_number=part_number,
                name=name,
                description=description,
                price=price,
                manufacturer=manufacturer,
                category=category,
                compatibility=compatibility,
                url=url,
                source="PartsTree",
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logging.error(f"Error parsing PartsTree part page {url}: {str(e)}")
            return None

    def parse_rotary_part(self, html: str, url: str) -> Optional[Part]:
        """Parse Rotary part detail page"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract part information based on actual Rotary.com structure
            product_info = soup.select_one('div.product-details')
            if not product_info:
                logging.warning(f"Could not find product info section on page: {url}")
                return None

            # Get part number from item number or SKU field
            part_number_elem = product_info.select_one('div.item-number') or product_info.select_one('span.sku')
            if not part_number_elem:
                logging.warning(f"Could not find part number on page: {url}")
                return None

            # Get other product details
            name_elem = product_info.select_one('h1.product-title')
            description_elem = product_info.select_one('div.description')
            price_elem = product_info.select_one('div.product-price')
            
            # Get specifications
            specs = {}
            specs_table = product_info.select_one('table.specifications')
            if specs_table and isinstance(specs_table, Tag):
                for row in specs_table.select('tr'):
                    cols = row.select('th, td')
                    if len(cols) == 2:
                        key = cols[0].get_text().strip()
                        value = cols[1].get_text().strip()
                        specs[key] = value

            # Get compatibility information
            compatibility = []
            fits_section = product_info.select_one('div.compatibility')
            if fits_section and isinstance(fits_section, Tag):
                compatibility = [
                    item.get_text().strip() 
                    for item in fits_section.select('li')
                    if isinstance(item, Tag)
                ]

            # Extract text values safely
            part_number = part_number_elem.get_text().strip() if isinstance(part_number_elem, Tag) else ''
            name = name_elem.get_text().strip() if name_elem and isinstance(name_elem, Tag) else None
            description = description_elem.get_text().strip() if description_elem and isinstance(description_elem, Tag) else None
            price_text = price_elem.get_text().strip() if price_elem and isinstance(price_elem, Tag) else ''

            # Parse price safely
            try:
                price = float(price_text.replace('$', '').replace(',', '')) if price_text else None
            except (ValueError, AttributeError):
                price = None
                logging.warning(f"Could not parse price from {price_text} on page: {url}")

            return Part(
                part_number=part_number,
                name=name,
                description=description,
                price=price,
                manufacturer=specs.get('Manufacturer', None),
                category=specs.get('Category', None),
                compatibility=compatibility,
                url=url,
                source="Rotary",
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logging.error(f"Error parsing Rotary part page {url}: {str(e)}")
            return None

    def parse_stens_part(self, html: str, url: str) -> Optional[Part]:
        """Parse Stens part detail page"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract part information based on actual Stens.com structure
            product_info = soup.select_one('div.product-info')
            if not product_info:
                logging.warning(f"Could not find product info section on page: {url}")
                return None

            # Get part number from SKU or product code field
            part_number_elem = product_info.select_one('span.sku') or product_info.select_one('div.product-code')
            if not part_number_elem:
                logging.warning(f"Could not find part number on page: {url}")
                return None

            # Get other product details
            name_elem = product_info.select_one('h1.product-title')
            description_elem = product_info.select_one('div.description')
            price_elem = product_info.select_one('div.price')
            
            # Get specifications
            specs = {}
            specs_table = product_info.select_one('table.specifications')
            if specs_table and isinstance(specs_table, Tag):
                for row in specs_table.select('tr'):
                    cols = row.select('th, td')
                    if len(cols) == 2:
                        key = cols[0].get_text().strip()
                        value = cols[1].get_text().strip()
                        specs[key] = value

            # Get compatibility information
            compatibility = []
            fits_section = product_info.select_one('div.compatibility')
            if fits_section and isinstance(fits_section, Tag):
                compatibility = [
                    item.get_text().strip() 
                    for item in fits_section.select('li')
                    if isinstance(item, Tag)
                ]

            # Extract text values safely
            part_number = part_number_elem.get_text().strip() if isinstance(part_number_elem, Tag) else ''
            name = name_elem.get_text().strip() if name_elem and isinstance(name_elem, Tag) else None
            description = description_elem.get_text().strip() if description_elem and isinstance(description_elem, Tag) else None
            price_text = price_elem.get_text().strip() if price_elem and isinstance(price_elem, Tag) else ''

            # Parse price safely
            try:
                price = float(price_text.replace('$', '').replace(',', '')) if price_text else None
            except (ValueError, AttributeError):
                price = None
                logging.warning(f"Could not parse price from {price_text} on page: {url}")

            return Part(
                part_number=part_number,
                name=name,
                description=description,
                price=price,
                manufacturer=specs.get('Manufacturer', None),
                category=specs.get('Category', None),
                compatibility=compatibility,
                url=url,
                source="Stens",
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logging.error(f"Error parsing Stens part page {url}: {str(e)}")
            return None

    def scrape_partstree(self, start_url: str) -> List[Part]:
        """
        Scrape parts information from PartsTree.com
        """
        logging.info(f"Starting PartsTree scrape from: {start_url}")
        parts = []
        visited_urls = set()
        urls_to_visit = [start_url]

        try:
            while urls_to_visit:
                url = urls_to_visit.pop(0)
                if url in visited_urls:
                    continue

                logging.info(f"Scraping URL: {url}")
                response = self.make_request(url)
                if not response:
                    continue

                visited_urls.add(url)
                
                # Parse the page
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # If this is a part detail page (contains part number), extract part information
                if any(marker in url for marker in ['/parts/', '/part/']):
                    part = self.parse_partstree_part(response.text, url)
                    if part:
                        parts.append(part)
                        logging.info(f"Successfully scraped part: {part.part_number}")

                # Find and add new URLs to visit
                for link in soup.select('a[href]'):
                    href = link.get('href')
                    if isinstance(href, str):
                        new_url = urljoin(url, href)
                        if (new_url.startswith('https://www.partstree.com/') and 
                            new_url not in visited_urls and 
                            self.can_fetch(new_url)):
                            urls_to_visit.append(new_url)

                # Save progress periodically
                if len(parts) % 100 == 0:
                    self.save_results(parts)

        except Exception as e:
            logging.error(f"Error in PartsTree scraping: {str(e)}")
        finally:
            self.save_results(parts)
            return parts

    def scrape_rotary(self, start_url: str) -> List[Part]:
        """
        Scrape parts information from Rotary
        """
        logging.info(f"Starting Rotary scrape from: {start_url}")
        parts = []
        visited_urls = set()
        urls_to_visit = [start_url]
        page_number = 1

        try:
            while urls_to_visit:
                url = urls_to_visit.pop(0)
                if url in visited_urls:
                    continue

                logging.info(f"Scraping URL: {url}")
                response = self.make_request(url)
                if not response:
                    continue

                visited_urls.add(url)
                
                # Parse the page
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # If this is a product detail page, extract part information
                if '/product/' in url or '/item/' in url:
                    part = self.parse_rotary_part(response.text, url)
                    if part:
                        parts.append(part)
                        logging.info(f"Successfully scraped part: {part.part_number}")

                # Find and add new URLs to visit
                for link in soup.select('a[href]'):
                    href = link.get('href')
                    if isinstance(href, str):
                        new_url = urljoin(url, href)
                        if (new_url.startswith('https://www.rotarycorp.com/') and 
                            new_url not in visited_urls and 
                            self.can_fetch(new_url)):
                            urls_to_visit.append(new_url)

                # Handle pagination - look for "Next" link or page numbers
                next_page = soup.select_one('a.next') or soup.select_one('a:contains("Next")')
                if next_page and next_page.get('href'):
                    href = next_page['href']
                    if isinstance(href, str):
                        next_url = urljoin(url, href)
                        if next_url not in visited_urls and self.can_fetch(next_url):
                            urls_to_visit.append(next_url)
                            page_number += 1
                            logging.info(f"Added page {page_number} to queue: {next_url}")

                # Save progress periodically
                if len(parts) % 100 == 0:
                    self.save_results(parts)

        except Exception as e:
            logging.error(f"Error in Rotary scraping: {str(e)}")
        finally:
            self.save_results(parts)
            return parts

    def scrape_stens(self, start_url: str) -> List[Part]:
        """
        Scrape parts information from Stens
        """
        logging.info(f"Starting Stens scrape from: {start_url}")
        parts = []
        visited_urls = set()
        urls_to_visit = [start_url]
        page_number = 1

        try:
            while urls_to_visit:
                url = urls_to_visit.pop(0)
                if url in visited_urls:
                    continue

                logging.info(f"Scraping URL: {url}")
                response = self.make_request(url)
                if not response:
                    continue

                visited_urls.add(url)
                
                # Parse the page
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # If this is a product detail page, extract part information
                if '/product/' in url or '/item/' in url:
                    part = self.parse_stens_part(response.text, url)
                    if part:
                        parts.append(part)
                        logging.info(f"Successfully scraped part: {part.part_number}")

                # Find and add new URLs to visit
                for link in soup.select('a[href]'):
                    href = link.get('href')
                    if isinstance(href, str):
                        new_url = urljoin(url, href)
                        if (new_url.startswith('https://www.stens.com/') and 
                            new_url not in visited_urls and 
                            self.can_fetch(new_url)):
                            urls_to_visit.append(new_url)

                # Handle pagination - look for "Next" link or page numbers
                next_page = soup.select_one('a.next') or soup.select_one('a:contains("Next")')
                if next_page and next_page.get('href'):
                    href = next_page['href']
                    if isinstance(href, str):
                        next_url = urljoin(url, href)
                        if next_url not in visited_urls and self.can_fetch(next_url):
                            urls_to_visit.append(next_url)
                            page_number += 1
                            logging.info(f"Added page {page_number} to queue: {next_url}")

                # Save progress periodically
                if len(parts) % 100 == 0:
                    self.save_results(parts)

        except Exception as e:
            logging.error(f"Error in Stens scraping: {str(e)}")
        finally:
            self.save_results(parts)
            return parts

    def save_results(self, parts: List[Part], filename: str = "parts_catalog_data.json"):
        """Save scraped results to a JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump([asdict(part) for part in parts], f, indent=4)
            logging.info(f"Results saved to {filename}")
        except Exception as e:
            logging.error(f"Error saving results: {str(e)}")

def main():
    scraper = PartsCatalogScraper()
    logging.info("Starting parts catalog scraping agent")
    
    # Start with PartsTree.com main catalog page
    parts = scraper.scrape_partstree('https://www.partstree.com/models/')
    logging.info(f"Completed PartsTree scraping with {len(parts)} parts found")

    # Continue with Rotary
    rotary_parts = scraper.scrape_rotary('https://www.rotarycorp.com/products')
    logging.info(f"Completed Rotary scraping with {len(rotary_parts)} parts found")

    # Finally scrape Stens
    stens_parts = scraper.scrape_stens('https://www.stens.com/products')
    logging.info(f"Completed Stens scraping with {len(stens_parts)} parts found")
    
    # Combine results
    all_parts = parts + rotary_parts + stens_parts
    scraper.save_results(all_parts)
    logging.info(f"Completed all scraping with total {len(all_parts)} parts found")

if __name__ == "__main__":
    main()