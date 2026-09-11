import requests, time, json, os, logging
from bs4 import BeautifulSoup
from datetime import datetime
from config import BASE_URL, MAX_PAGES, REQUEST_DELAY, RAW_DATA_PATH, HEADERS

def get_page(url):
    time.sleep(REQUEST_DELAY)
    for attempt in range(3):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(3)
    logging.error(f"Failed to fetch {url} after 3 attempts")
    return None

def safe_get(element):
    return element.get_text(strip=True) if element else None

def extract_jobs(soup):
    jobs = []
    jobs_cards = soup.find_all("article", class_=lambda c: c and "job-card" in c)
    for job in jobs_cards:
        job_data = {
            "job_title": job.find("a", {"data-qa": "job-card-title"}).get_text(strip=True),
            "salary": safe_get(job.find("li", {"data-qa": "job-metadata-salary"})),
            "location": safe_get(job.find("li", {"data-qa": "job-metadata-location"})),
            "posted_date": safe_get(job.find("div", {"data-qa": "job-posted-by"})),
            "job_url": "https://www.reed.co.uk" + job.find("a", {"data-qa": "job-card-title"})["href"],
            "scraped_at": datetime.now().isoformat()
        }
        jobs.append(job_data)
    if jobs:
        return jobs

def scrape_all_pages():
    all_jobs = []
    page = 1
    while True:
        url = BASE_URL if page == 1 else f"{BASE_URL}?pageno={page}"
        if page > MAX_PAGES:
            break
        soup = get_page(url)
        if soup is None:
            print(f"Skipping page {page} - failed to fetch")
            page += 1
            continue
        jobs = extract_jobs(soup)
        if not jobs:
            break
        all_jobs.extend(jobs)
        print(f"Scraped page {page}, {len(jobs)} jobs found")
        page += 1
    return all_jobs

if __name__ == "__main__":
    all_jobs = scrape_all_pages()
    print(f"Total jobs scraped: {len(all_jobs)}")
    print(all_jobs[0])
    os.makedirs("data", exist_ok=True)
    with open(RAW_DATA_PATH, "w") as f:
        json.dump(all_jobs, f, indent=2)
    print(f"Raw data saved to {RAW_DATA_PATH}")