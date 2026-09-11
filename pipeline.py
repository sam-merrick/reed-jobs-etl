import logging
from scraper import scrape_all_pages
from transform import load_raw_data, transform, save_parquet
from config import RAW_DATA_PATH, OUTPUT_PATH
import json, os

logging.basicConfig(
    level= logging.INFO,
    format= '%(asctime)s - %(levelname)s - %(message)s'
)

def run():
    logging.info("Pipeline started")

    # Extract
    logging.info("Starting scrape...")
    all_jobs = scrape_all_pages()
    os.makedirs("data", exist_ok=True)
    with open(RAW_DATA_PATH, "w") as f:
        json.dump(all_jobs, f, indent=2)
    logging.info(f"Scraped {len(all_jobs)} raw jobs, saved to {RAW_DATA_PATH}")

    # Transform
    logging.info("Starting transform...")
    df_raw = load_raw_data(RAW_DATA_PATH)
    df_clean = transform(df_raw)
    logging.info(f"Transform complete - {len(df_clean)} rows after cleaning")

    # Load
    logging.info("Saving to Parquet...")
    save_parquet(df_clean, OUTPUT_PATH)
    logging.info("Pipeline complete")

if __name__ == "__main__":
    run()