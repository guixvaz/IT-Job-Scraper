# Swiss IT Job Scraper 🇨🇭

An automated, OOP-architected web scraper built with Python and Playwright to aggregate entry-level IT, Werkstudent, and Praktikum positions in Switzerland. 

I built this tool to streamline my own job search alongside my Wirtschaftsinformatik studies at FHNW, specifically filtering for roles with a maximum 60% workload to accommodate lecture days.

## Tech Stack
* **Language:** Python 3.11+
* **Browser Automation:** Playwright (Headless Chromium)
* **Database & ORM:** SQLite 3, SQLModel / SQLAlchemy
* **CLI UI:** Rich

## Architecture
The project implements the **Factory Design Pattern** to ensure modularity and scalability. 
* A base `JobScraper` interface defines the core contract.
* Platform-specific scrapers (`LinkedInScraper`, `JobsChScraper`) handle the unique DOM structures and query parameters of each site.
* **State Management:** A local SQLite database tracks scraped `job_id`s to ensure only net-new opportunities are surfaced in the terminal UI, preventing duplicate alerts across multiple runs.
