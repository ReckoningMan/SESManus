import requests
from bs4 import BeautifulSoup
import logging
import time
import json
from typing import List, Dict, Optional
from datetime import datetime
from urllib.robotparser import RobotFileParser
from dataclasses import dataclass, asdict
import random
from urllib.parse import urljoin

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
            
            # Extract part information (adjust selectors based on actual HTML structure)
            part_number = soup.select_one('.part-number')
            name = soup.select_one('.part-name')
            description = soup.select_one('.part-description')
            price = soup.select_one('.part-price')
            manufacturer = soup.select_one('.manufacturer')
            category = soup.select_one('.category')
            compatibility = [item.text.strip() for item in soup.select('.compatibility-list li')]

            if not part_number:
                logging.warning(f"Could not find part number on page: {url}")
                return None

            return Part(
                part_number=part_number.text.strip(),
                name=name.text.strip() if name else None,
                description=description.text.strip() if description else None,
                price=float(price.text.strip().replace('$', '')) if price else None,
                manufacturer=manufacturer.text.strip() if manufacturer else None,
                category=category.text.strip() if category else None,
                compatibility=compatibility,
                url=url,
                source="PartsTree",
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logging.error(f"Error parsing part page {url}: {str(e)}")
            return None

    def parse_rotary_part(self, html: str, url: str) -> Optional[Part]:
        """Parse Rotary part detail page"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract part information (adjust selectors based on actual HTML structure)
            part_number = soup.select_one('.product-number')
            name = soup.select_one('.product-name')
            description = soup.select_one('.product-description')
            price = soup.select_one('.product-price')
            manufacturer = soup.select_one('.manufacturer')
            category = soup.select_one('.category')
            compatibility = [item.text.strip() for item in soup.select('.compatibility li')]

            if not part_number:
                logging.warning(f"Could not find part number on page: {url}")
                return None

            return Part(
                part_number=part_number.text.strip(),
                name=name.text.strip() if name else None,
                description=description.text.strip() if description else None,
                price=float(price.text.strip().replace('$', '')) if price else None,
                manufacturer=manufacturer.text.strip() if manufacturer else None,
                category=category.text.strip() if category else None,
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
            
            # Extract part information (adjust selectors based on actual HTML structure)
            part_number = soup.select_one('.sku')
            name = soup.select_one('.product-name')
            description = soup.select_one('.description')
            price = soup.select_one('.price')
            manufacturer = soup.select_one('.manufacturer')
            category = soup.select_one('.category')
            compatibility = [item.text.strip() for item in soup.select('.compatibility-list li')]

            if not part_number:
                logging.warning(f"Could not find part number on page: {url}")
                return None

            return Part(
                part_number=part_number.text.strip(),
                name=name.text.strip() if name else None,
                description=description.text.strip() if description else None,
                price=float(price.text.strip().replace('$', '')) if price else None,
                manufacturer=manufacturer.text.strip() if manufacturer else None,
                category=category.text.strip() if category else None,
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
                
                # If this is a part detail page, extract part information
                if '/parts/' in url:
                    part = self.parse_partstree_part(response.text, url)
                    if part:
                        parts.append(part)
                        logging.info(f"Successfully scraped part: {part.part_number}")

                # Find and add new URLs to visit
                for link in soup.find_all('a', href=True):
                    new_url = urljoin(url, link['href'])
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
                
                # If this is a part detail page, extract part information
                if '/product/' in url:
                    part = self.parse_rotary_part(response.text, url)
                    if part:
                        parts.append(part)
                        logging.info(f"Successfully scraped part: {part.part_number}")

                # Find and add new URLs to visit
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if isinstance(href, str):
                        new_url = urljoin(url, href)
                        if (new_url.startswith('https://www.rotarycorp.com/') and 
                            new_url not in visited_urls and 
                            self.can_fetch(new_url)):
                            urls_to_visit.append(new_url)

                # Handle pagination
                next_page = soup.select_one('.pagination .next')
                if next_page and 'href' in next_page.attrs:
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
                
                # If this is a part detail page, extract part information
                if '/product/' in url:
                    part = self.parse_stens_part(response.text, url)
                    if part:
                        parts.append(part)
                        logging.info(f"Successfully scraped part: {part.part_number}")

                # Find and add new URLs to visit
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if isinstance(href, str):
                        new_url = urljoin(url, href)
                        if (new_url.startswith('https://www.stens.com/') and 
                            new_url not in visited_urls and 
                            self.can_fetch(new_url)):
                            urls_to_visit.append(new_url)

                # Handle pagination
                next_page = soup.select_one('.pagination .next')
                if next_page and 'href' in next_page.attrs:
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