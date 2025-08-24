#!/usr/bin/env python3
"""
Zero-Cost LinkedIn Job Scraper
Advanced LinkedIn scraping with multiple fallback methods - completely free!
"""

import time
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import logging
from datetime import datetime, timedelta
import json
import re
from urllib.parse import urlencode, quote_plus
import feedparser
from fake_useragent import UserAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkedInScraperFree:
    """
    Zero-cost LinkedIn job scraper with multiple methods and fallbacks
    """
    
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.free_proxies = []
        self.setup_session()
        
    def setup_session(self):
        """Setup requests session with rotating user agents"""
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_free_proxies(self):
        """Get free proxy list (optional - can work without proxies)"""
        try:
            # Free proxy sources (optional)
            proxy_urls = [
                'https://www.proxy-list.download/api/v1/get?type=http',
                'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all'
            ]
            
            for url in proxy_urls:
                try:
                    response = requests.get(url, timeout=10)
                    proxies = response.text.strip().split('\n')
                    self.free_proxies.extend([f"http://{proxy}" for proxy in proxies[:5]])
                    break
                except:
                    continue
                    
            logger.info(f"Loaded {len(self.free_proxies)} free proxies")
        except Exception as e:
            logger.warning(f"Could not load free proxies: {e}")
            self.free_proxies = []
    
    def create_stealth_driver(self):
        """Create a stealth Chrome driver for LinkedIn scraping"""
        options = Options()
        
        # Stealth options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f'--user-agent={self.ua.random}')
        
        # Performance options
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript')  # LinkedIn works without JS for basic scraping
        
        # Optional: headless mode
        # options.add_argument('--headless')
        
        try:
            # Use webdriver-manager to automatically handle Chrome driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

            # Execute script to remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            return driver
        except Exception as e:
            logger.error(f"Could not create Chrome driver: {e}")
            logger.info("Make sure Chrome browser is installed on your system")
            return None
    
    def method_1_guest_api(self, keywords, location, max_results=25, time_filter='r3600', work_type='2'):
        """
        Method 1: LinkedIn Guest API (Free, No Authentication)
        Most reliable free method with ultra-recent job filtering

        Args:
            time_filter:
                - 'r300' = Last 5 minutes
                - 'r600' = Last 10 minutes
                - 'r1800' = Last 30 minutes
                - 'r3600' = Last 1 hour (default)
                - 'r86400' = Last 24 hours
            work_type:
                - '1' = On-site
                - '2' = Remote
                - '3' = Hybrid
        """
        logger.info(f"🔍 Method 1: LinkedIn Guest API (Time: {time_filter}, Location: {location})")

        jobs = []
        start = 0

        while len(jobs) < max_results and start < 200:
            try:
                # LinkedIn guest job search endpoint with ultra-recent filtering
                params = {
                    'keywords': keywords,
                    'location': location,
                    'start': start,
                    'count': 25,
                    'f_TPR': time_filter,  # Ultra-recent time filter
                    'f_WT': work_type,  # Work type filter
                }
                
                url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?{urlencode(params)}"
                
                # Rotate user agent
                self.session.headers['User-Agent'] = self.ua.random
                
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 429:
                    logger.warning("Rate limited, waiting...")
                    time.sleep(random.uniform(30, 60))
                    continue
                    
                if response.status_code != 200:
                    logger.warning(f"API returned {response.status_code}")
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = soup.find_all('div', class_='base-search-card')
                
                if not job_cards:
                    logger.info("No more jobs found")
                    break
                
                for card in job_cards:
                    try:
                        job = self.parse_job_card(card)
                        if job:
                            jobs.append(job)
                            
                        if len(jobs) >= max_results:
                            break
                            
                    except Exception as e:
                        logger.warning(f"Error parsing job card: {e}")
                        continue
                
                start += 25
                
                # Respectful delay
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                logger.error(f"Method 1 error: {e}")
                break
        
        logger.info(f"✅ Method 1 found {len(jobs)} jobs")
        return jobs
    
    def method_2_selenium_stealth(self, keywords, location, max_results=25):
        """
        Method 2: Selenium with Stealth (Free, Browser Automation)
        Backup method when API fails
        """
        logger.info("🔍 Method 2: Selenium Stealth")
        
        driver = self.create_stealth_driver()
        if not driver:
            return []
        
        jobs = []
        
        try:
            # Build LinkedIn job search URL
            search_params = {
                'keywords': keywords,
                'location': location,
                'f_TPR': 'r86400',  # Last 24 hours
                'f_WT': '2',  # Remote
            }
            
            search_url = f"https://www.linkedin.com/jobs/search?{urlencode(search_params)}"
            
            logger.info(f"Navigating to: {search_url}")
            driver.get(search_url)
            
            # Wait for jobs to load
            time.sleep(random.uniform(3, 6))
            
            # Scroll to load more jobs
            for i in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2, 4))
            
            # Find job cards
            job_elements = driver.find_elements(By.CSS_SELECTOR, '[data-entity-urn*="jobPosting"]')
            
            for element in job_elements[:max_results]:
                try:
                    job = self.parse_selenium_job(element)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.warning(f"Error parsing selenium job: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Method 2 error: {e}")
        finally:
            driver.quit()
        
        logger.info(f"✅ Method 2 found {len(jobs)} jobs")
        return jobs
    
    def method_3_rss_feeds(self, keywords, location, max_results=25):
        """
        Method 3: LinkedIn RSS Feeds (Free, Most Reliable)
        Fallback method - very stable
        """
        logger.info("🔍 Method 3: RSS Feeds")
        
        jobs = []
        
        try:
            # LinkedIn job alert RSS (if available)
            # Alternative: Use Google Jobs RSS
            google_query = f"site:linkedin.com/jobs {keywords} {location}"
            rss_url = f"https://www.google.com/alerts/feeds/00000000000000000000/0000000000000000000"
            
            # For now, use a simpler approach - scrape LinkedIn job sitemap
            sitemap_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            
            # This method would need RSS feed setup
            logger.info("RSS method requires pre-configured feeds")
            
        except Exception as e:
            logger.error(f"Method 3 error: {e}")
        
        logger.info(f"✅ Method 3 found {len(jobs)} jobs")
        return jobs
    
    def parse_job_card(self, card):
        """Parse job information from LinkedIn job card"""
        try:
            # Extract job details
            title_elem = card.find('h3', class_='base-search-card__title')
            title = title_elem.get_text(strip=True) if title_elem else "N/A"
            
            company_elem = card.find('h4', class_='base-search-card__subtitle')
            company = company_elem.get_text(strip=True) if company_elem else "N/A"
            
            location_elem = card.find('span', class_='job-search-card__location')
            location = location_elem.get_text(strip=True) if location_elem else "N/A"
            
            link_elem = card.find('a', class_='base-card__full-link')
            job_url = link_elem.get('href') if link_elem else "N/A"
            
            # Extract job ID from URL
            job_id = re.search(r'jobs/view/(\d+)', job_url)
            job_id = job_id.group(1) if job_id else "N/A"
            
            # Extract posting date
            time_elem = card.find('time')
            posted_date = time_elem.get('datetime') if time_elem else datetime.now().isoformat()
            
            return {
                'id': job_id,
                'title': title,
                'company': company,
                'location': location,
                'job_url': job_url,
                'posted_date': posted_date,
                'site': 'linkedin',
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Error parsing job card: {e}")
            return None
    
    def parse_selenium_job(self, element):
        """Parse job from Selenium element"""
        try:
            title = element.find_element(By.CSS_SELECTOR, 'h3 a').text.strip()
            company = element.find_element(By.CSS_SELECTOR, 'h4 a').text.strip()
            location = element.find_element(By.CSS_SELECTOR, '[class*="job-search-card__location"]').text.strip()
            job_url = element.find_element(By.CSS_SELECTOR, 'h3 a').get_attribute('href')
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'job_url': job_url,
                'site': 'linkedin',
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Error parsing selenium job: {e}")
            return None
    
    def scrape_jobs(self, keywords, location="Remote", max_results=50, time_filter='r3600', work_type='2'):
        """
        Main scraping method with multiple fallbacks and ultra-recent filtering

        Args:
            time_filter:
                - 'r300' = Last 5 minutes (ultra-recent for first applicant advantage)
                - 'r600' = Last 10 minutes
                - 'r1800' = Last 30 minutes
                - 'r3600' = Last 1 hour (default)
                - 'r86400' = Last 24 hours
            work_type:
                - '1' = On-site
                - '2' = Remote (default)
                - '3' = Hybrid
        """
        logger.info(f"🚀 Starting ULTRA-RECENT LinkedIn job scrape for '{keywords}' in '{location}'")
        logger.info(f"⏰ Time filter: {time_filter} | Work type: {work_type}")

        all_jobs = []

        # Method 1: Guest API (Primary) with ultra-recent filtering
        try:
            jobs_1 = self.method_1_guest_api(keywords, location, max_results//2, time_filter, work_type)
            all_jobs.extend(jobs_1)
        except Exception as e:
            logger.error(f"Method 1 failed: {e}")
        
        # Method 2: Selenium (Backup) - Skip if network issues
        if len(all_jobs) < max_results//2:
            try:
                jobs_2 = self.method_2_selenium_stealth(keywords, location, max_results//2)
                all_jobs.extend(jobs_2)
            except Exception as e:
                logger.warning(f"Method 2 (Selenium) skipped due to network/driver issues: {e}")
                # Continue with Method 1 results only
        
        # Remove duplicates
        seen_urls = set()
        unique_jobs = []
        
        for job in all_jobs:
            if job.get('job_url') not in seen_urls:
                seen_urls.add(job.get('job_url'))
                unique_jobs.append(job)
        
        logger.info(f"🎉 Total unique jobs found: {len(unique_jobs)}")
        
        return pd.DataFrame(unique_jobs)

def test_linkedin_scraper():
    """Test the free LinkedIn scraper"""
    scraper = LinkedInScraperFree()
    
    # Test with your job preferences
    jobs_df = scraper.scrape_jobs(
        keywords="java developer",
        location="Remote",
        max_results=20
    )
    
    print(f"Found {len(jobs_df)} LinkedIn jobs!")
    
    if len(jobs_df) > 0:
        print("\nSample jobs:")
        for i, job in jobs_df.head(5).iterrows():
            print(f"- {job['title']} at {job['company']} ({job['location']})")
    
    return jobs_df

if __name__ == "__main__":
    test_linkedin_scraper()
