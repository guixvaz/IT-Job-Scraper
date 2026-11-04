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
                        "location": job.location,
                        "workload": job.workload,
                        "url": job.url
                    })
            session.commit()

        browser.close()

    # Terminal UI
    if new_jobs_found:
        # Create a professional, spaced-out table
        table = Table(
            title="New IT Student Opportunities (Max 60%)",
            show_header=True, 
            header_style="bold magenta",
            padding=(1, 2) # Adds horizontal breathing room between columns
        )
        
        # Enforce max_width and overflow="ellipsis" to prevent text from breaking the layout
        table.add_column("Title (Ctrl+Click to open)", style="cyan", max_width=150, overflow="ellipsis")
        table.add_column("Company", style="white", max_width=25, overflow="ellipsis")
        table.add_column("Location", style="dim", max_width=20, overflow="ellipsis")
        table.add_column("Workload", style="yellow", justify="right")

        for job in new_jobs_found:
            # This rich syntax turns the title into a clickable hyperlink in VS Code / modern terminals!
            clickable_title = f"[link={job['url']}]{job['title']}[/link]"
            
            table.add_row(
                clickable_title, 
                job["company"], 
                job["location"], 
                job["workload"]
            )

        console.print(table)
    else:
        console.print("[bold yellow]No new jobs found matching your criteria.[/bold yellow]")

if __name__ == "__main__":
    main()