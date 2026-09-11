BASE_URL = "https://www.reed.co.uk/jobs/data-engineer-jobs"
MAX_PAGES = 20
REQUEST_DELAY = 1  # seconds between requests
RAW_DATA_PATH = "data/raw_jobs.json"
OUTPUT_PATH = "data/jobs_clean.parquet"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (educational scraper project)"
}