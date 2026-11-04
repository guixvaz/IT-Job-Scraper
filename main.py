from playwright.sync_api import sync_playwright
from sqlmodel import Session, select
from rich.console import Console
from rich.table import Table
from scrapers import ScraperFactory
from db import create_db_and_tables, engine, JobListing

def main():
    create_db_and_tables()
    console = Console()
    new_jobs_found = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context()
        page = context.new_page()

        scraper = ScraperFactory.get_scraper("jobs.ch", page)
        scraped_jobs = scraper.scrape()

        with Session(engine) as session:
            for job in scraped_jobs:
                # Check if this exact job is already in the database
                existing_job = session.exec(select(JobListing).where(JobListing.job_id == job.job_id)).first()
                if not existing_job:
                    session.add(job)
                    # Extract a plain dictionary version for the UI so it survives the closed session
                    new_jobs_found.append({
                        "title": job.title,
                        "company": job.company,
                        "workload": job.workload,
                        "url": job.url
                    })
            session.commit()

        browser.close()

    # Terminal UI
    if new_jobs_found:
        table = Table(title="New IT Opportunities (Max 60%)")
        table.add_column("Title", style="cyan", no_wrap=True)
        table.add_column("Company", style="magenta")
        table.add_column("Workload", style="yellow")
        table.add_column("Link", style="blue")

        for job in new_jobs_found:
            # We now access dictionary keys instead of database object attributes
            table.add_row(job["title"][:30] + "...", job["company"][:20], job["workload"], job["url"])

        console.print(table)
    else:
        console.print("[bold yellow]No new jobs found matching your criteria.[/bold yellow]")

if __name__ == "__main__":
    main()