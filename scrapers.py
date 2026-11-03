import re
from abc import ABC, abstractmethod
from typing import List
from playwright.sync_api import Page
from db import JobListing

class JobScraper(ABC):
    def __init__(self, page: Page, max_workload: int = 60):
        self.page = page
        self.max_workload = max_workload
        self.keywords = ["Werkstudent IT", "Praktikum IT", "IT Support"]

    @abstractmethod
    def scrape(self) -> List[JobListing]:
        pass

    def is_workload_acceptable(self, workload_str: str) -> bool:
        """Parses strings like '40 - 60%' or '100%' and checks against max_workload."""
        if not workload_str:
            return False
            
        # Find all numbers in the string
        numbers = [int(n) for n in re.findall(r'\d+', workload_str)]
        if not numbers:
            return True # If it just says "Part-time", it is kept to review manually
            
        # If the minimum workload mentioned is <= max workload, keep it
        min_workload = min(numbers)
        return min_workload <= self.max_workload

class JobsChScraper(JobScraper):
    def scrape(self) -> List[JobListing]:
        jobs = []
        for keyword in self.keywords:
            formatted_keyword = keyword.replace(" ", "%20")
            page_num = 1
            max_pages = 10  # Safety limit so it doesn't run forever

            while page_num <= max_pages:
                # Add the page parameter to the URL
                url = f"https://www.jobs.ch/en/vacancies/?term={formatted_keyword}&page={page_num}"
                print(f"\n--- Scraping jobs.ch for: '{keyword}' (Page {page_num}) ---")
                
                self.page.goto(url)
                
                try:
                    # Wait for cards to load. If it times out, we've hit the end of the results.
                    self.page.wait_for_selector("a[data-cy='job-link']", timeout=5000)
                    self.page.wait_for_timeout(1000) 
                except Exception:
                    print(f"No more jobs found for '{keyword}'. Moving to next keyword.")
                    break  # Break the while loop to move to the next keyword
                
                job_cards = self.page.locator("a[data-cy='job-link']").all()
                print(f"Total job cards detected on page {page_num}: {len(job_cards)}")
                
                if len(job_cards) == 0:
                    break  # Extra safety check

                for card in job_cards:
                    try:
                        title = card.get_attribute("title")
                        href = card.get_attribute("href")
                        full_url = f"https://www.jobs.ch{href}" if href and href.startswith("/") else href
                        
                        raw_id = card.get_attribute("id") 
                        if raw_id:
                            job_id = raw_id 
                        else:
                            clean_href = href.rstrip('/') if href else ""
                            job_id = f"jobsch_{clean_href.split('/')[-1]}" if clean_href else "unknown_id"

                        # 1. Enforce strict IT relevance
                        title_lower = (title or "").lower()
                        valid_it_terms = ["it", "software", "developer", "entwickler", "support", "informatik", "system", "data", "web"]
                        if not any(term in title_lower for term in valid_it_terms):
                            continue # Silently skip non-IT jobs to keep the terminal clean

                        # 2. Extract remaining fields
                        company_locator = card.locator("p.fw_bold")
                        company = company_locator.first.inner_text() if company_locator.count() > 0 else "Unknown"
                        
                        workload_locator = card.locator("span:has-text('Workload:') + p")
                        workload_text = workload_locator.first.inner_text() if workload_locator.count() > 0 else "100%"
                        
                        location_locator = card.locator("span:has-text('Place of work:') + p")
                        location = location_locator.first.inner_text() if location_locator.count() > 0 else "Unknown"

                        # 3. Apply the 60% FHNW workload filter
                        if self.is_workload_acceptable(workload_text):
                            job = JobListing(
                                job_id=job_id,
                                title=title,
                                company=company,
                                location=location,
                                workload=workload_text,
                                url=full_url,
                                platform="jobs.ch"
                            )
                            jobs.append(job)
                            
                    except Exception as e:
                        print(f"  -> ERROR parsing this card: {e}")
                        continue
                
                # Increment the page number to scrape the next page in the next loop iteration
                page_num += 1
                
        return jobs

class ScraperFactory:
    @staticmethod
    def get_scraper(platform: str, page: Page) -> JobScraper:
        if platform.lower() == "jobs.ch":
            return JobsChScraper(page)
        raise ValueError(f"Unknown platform: {platform}")