# IT Student Job Scraper & AI Evaluator

A robust, OOP-architected Python automation tool designed to scrape, filter, and intelligently evaluate part-time IT job opportunities in Switzerland. 

I built this tool to streamline my own job search alongside my Wirtschaftsinformatik studies at FHNW. This tool extracts job listings, enforces strict workload limits (max 60%), and leverages the Google Gemini API to read full job descriptions and match them against a specific technical and methodological skill set.

## Features

* **Architectural Factory Pattern:** Highly modular design (`ScraperFactory`) allowing seamless integration of new job platforms. Currently supports `jobs.ch`.
* **AI-Powered Qualification Matching:** Uses **Google Gemini 3.5 Flash Lite** and Pydantic structured outputs to evaluate raw job descriptions in background tabs, returning strict JSON boolean matches based on candidate skills.
* **Smart Workload Filtering:** Automatically parses text strings (e.g., "40 - 100%") and rejects any role exceeding the 60% workload cap to protect university lecture days.
* **Stateful Database Tracking:** Utilizes **SQLite** and **SQLModel** to track unique vacancy IDs, preventing duplicate jobs from appearing across multiple runs.
* **Advanced Terminal UI:** Uses the **Rich** library to render a clean, padded terminal grid featuring clickable job title hyperlinks and truncated overflow text.
* **Headless Background Processing:** Built on **Playwright** with isolated browser contexts to handle multi-page pagination and background-tab text extraction without triggering bot protections.

## Tech Stack

* **Language:** Python 3.10+
* **Web Scraping:** Playwright
* **AI / LLM:** Google GenAI SDK (`gemini-3.5-flash-lite`), Pydantic
* **Database:** SQLModel, SQLite 3
* **Interface:** Rich
* **Environment:** python-dotenv

## Project Structure

```text
├── main.py           # Orchestrates the browser context, database session, and Rich UI
├── scrapers.py       # Abstract JobScraper base class and JobsChScraper implementation
├── evaluator.py      # GeminiEvaluator class with strict AI system prompts
├── db.py             # SQLModel schemas and SQLite engine initialization
├── .env              # Secure environment variables (ignored by Git)
├── .gitignore        # Git ignore rules
└── README.md