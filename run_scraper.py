from playwright.sync_api import sync_playwright
from sqlmodel import Session, select
from src.db import engine, JobListing, SQLModel
from src.scrapers import ScraperFactory

def create_db_and_tables():
    # Initializes the database schema
    SQLModel.metadata.create_all(engine)

def main():
    # 1. Ensure the tables exist in data/jobs.db
    create_db_and_tables()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context()
        page = context.new_page()

        # 2. Run the scraper
        scraper = ScraperFactory.get_scraper("jobs.ch", page)
        scraped_jobs = scraper.scrape()
        
        # 3. Save the results to the database
        if scraped_jobs:
            with Session(engine) as session:
                saved_count = 0
                for job in scraped_jobs:
                    # Check if the job already exists to prevent duplicate errors
                    existing_job = session.exec(
                        select(JobListing).where(JobListing.job_id == job.job_id)
                    ).first()
                    
                    if not existing_job:
                        session.add(job)
                        saved_count += 1
                        
                session.commit()
            print(f"\n--- SUCCESS: Saved {saved_count} new jobs to the database! ---")
        else:
            print("\n--- No jobs matched your criteria this run. ---")

        browser.close()

if __name__ == "__main__":
    main()