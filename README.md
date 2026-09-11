# Reed.co.uk Data Engineer Jobs — ETL Pipeline

## Overview
A Python ETL pipeline that scrapes live Data Engineer job listings 
from reed.co.uk, cleans and structures the raw data, and outputs 
a Parquet file ready for analysis.

Built to demonstrate real-world data sourcing from an unstructured 
web source — unlike datasets that start clean and pre-structured, 
this pipeline handles genuinely messy data including inconsistent 
salary formats, relative date strings, and missing values.

## What it does

**Extract:** Scrapes up to 20 pages of Data Engineer job listings 
from reed.co.uk with polite rate limiting and automatic retry logic. 
Raw data saved as JSON (Bronze layer).

**Transform:** Cleans and structures each field:
- Salary parsed into min, max, type (annual/daily/hourly), 
  currency, benefits flag, and negotiable flag
- Location split into city and county
- Posted date parsed from relative ("3 days ago") and absolute 
  ("27 August") formats into ISO date strings
- Recruiter/company extracted from posted date string
- Seniority level inferred from job title

**Load:** Cleaned DataFrame written to Parquet (Silver layer).

## Project structure

├── config.py # All configuration in one place
├── scraper.py # Extract — scrapes reed.co.uk
├── transform.py # Transform — cleans and structures raw data
├── pipeline.py # Orchestrates extract → transform → load
└── data/ # Generated on run, git ignored
├── raw_jobs.json # Raw scraped data (Bronze)
└── jobs_clean.parquet # Cleaned output (Silver)


## Output columns

| Column | Description |
|---|---|
| job_title | Raw job title |
| job_url | Link to full listing |
| scraped_at | Timestamp of scrape |
| salary_min | Minimum salary (float) |
| salary_max | Maximum salary (float) |
| salary_type | annual / daily / hourly |
| salary_currency | GBP or USD |
| includes_benefits | Boolean |
| negotiable | Boolean |
| salary_raw | Original salary string |
| city | Parsed city |
| county | Parsed county |
| posted_date | ISO format date |
| posted_by | Recruiter or company name |
| seniority | Senior / Mid / Junior / Lead / Principal |
| processed_at | Timestamp of transform |

## How to run

```bash
pip install requests beautifulsoup4 pandas pyarrow apscheduler

python pipeline.py
```

## Key concepts demonstrated
- Web scraping with BeautifulSoup and pagination handling
- Polite scraping with rate limiting and retry logic
- Raw data preservation before transformation (Bronze principle)
- Complex string parsing with regex (salary, dates)
- NaN-safe cleaning functions across all fields
- Modular ETL structure — scraper, transform, pipeline, config
- Parquet output for efficient downstream consumption

## Tech stack
- Python
- BeautifulSoup4
- Pandas
- Requests
- PyArrow

## Data source
Reed.co.uk — UK job listings
https://www.reed.co.uk/jobs/data-engineer-jobs