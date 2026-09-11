import json, re, os
import pandas as pd
from datetime import datetime, timedelta
from config import RAW_DATA_PATH, OUTPUT_PATH

def load_raw_data(path):
    with open(path, "r") as f:
        data = json.load(f)
    return pd.DataFrame(data)

def clean_salary(salary_str):

    result = {
        "salary_min": None,
        "salary_max": None,
        "salary_type": None,
        "salary_currency": "GBP",
        "includes_benefits": False,
        "negotiable": False,
        "salary_raw": salary_str
    }

    if not salary_str:
        return result

    s = salary_str.lower().strip()

    non_salary = ["salary not specified", "competitive salary", "training course"]
    if any(phrase in s for phrase in non_salary):
        return result

    numbers = re.findall(r'\d[\d,]*\.?\d*', salary_str)
    cleaned_numbers = [float(num.replace(",", "")) for num in numbers]

    if len(cleaned_numbers) == 1:
        result["salary_min"] = cleaned_numbers[0]
        result["salary_max"] = cleaned_numbers[0]
    elif len(cleaned_numbers) >= 2:
        result["salary_min"] = cleaned_numbers[0]
        result["salary_max"] = cleaned_numbers[1]

    if "per annum" in result["salary_raw"]:
        result["salary_type"] = "annual"
    elif "per day" in result["salary_raw"]:
        result["salary_type"] = "daily"
    elif "per hour" in result["salary_raw"]:
        result["salary_type"] = "hourly"

    result["includes_benefits"] = "inc benefits" in s

    result["negotiable"] = "negotiable" in s

    if "usd" in s:
        result["salary_currency"] = "USD"

    # Spotted a wide salary range in the data, this handles the edge case
    if result["salary_min"] and result["salary_max"]:
        if result["salary_max"] > result["salary_min"] * 5:
            result["salary_max"] = None

    return result

def clean_location(location_str):

    result = {
        "city": None,
        "county": None
    }

    if not location_str or not isinstance(location_str, str) or not location_str.strip():
        return result

    split_location = location_str.split(",")

    if len(split_location) == 1:
        result["city"] = split_location[0].strip()
    elif len(split_location) == 2:
        result["city"] = split_location[0].strip()
        result["county"] = split_location[1].strip()
    else:
        result["city"] = split_location[0].strip()

    return result

def clean_posted_date(date_str, scraped_at):

    result = {
        "posted_date": None,
        "posted_by": None
    }

    if not isinstance(date_str, str) or not isinstance(scraped_at, str):
        return result

    reference_date = datetime.fromisoformat(scraped_at).date()

    split_posted_date = date_str.split("by")

    date_part = split_posted_date[0].strip()
    posted_by = split_posted_date[1].strip()

    if "today" in date_part.lower():
        parsed_date = reference_date
    elif "yesterday" in date_part.lower():
        parsed_date = reference_date - timedelta(days=1)
    elif "hours ago" in date_part.lower():
        parsed_date = reference_date
    elif "days ago" in date_part.lower():
        days = int(re.search(r'\d+', date_part).group())
        parsed_date = reference_date - timedelta(days=days)
    else:
        try:
            parts = date_part.strip().split(" ")
            day = int(parts[0])
            month_num = datetime.strptime(parts[1], "%B").month
            parsed_date = datetime(datetime.now().year, month_num, day).date()
            if parsed_date > datetime.now().date():
                parsed_date = datetime(datetime.now().year - 1, month_num, day).date()
        except (ValueError, IndexError):
            parsed_date = None
            result["posted_date"] = None
            result["posted_by"] = posted_by
            return result

    result["posted_date"] = str(parsed_date)
    result["posted_by"] = posted_by
    return result

def extract_seniority(title_str):

    result = {
        "seniority": None
    }

    if not isinstance(title_str, str) or not title_str.strip():
        return result

    s = title_str.lower().strip()

    if "senior" in s:
        result["seniority"] = "Senior"
    elif "principal" in s:
        result["seniority"] = "Principal"
    elif "lead" in s:
        result["seniority"] = "Lead"
    elif "junior" in s:
        result["seniority"] = "Junior"
    else:
        result["seniority"] = "Mid"

    return result

def transform(df):
    df =  df[df["job_title"].str.contains("data engineer", case=False, na=False)]

    salary_parsed = df["salary"].apply(clean_salary)
    salary_df = pd.DataFrame(salary_parsed.tolist())
    df = pd.concat([df, salary_df], axis=1)

    location_parsed = df["location"].apply(clean_location)
    location_df = pd.DataFrame(location_parsed.tolist())
    df = pd.concat([df, location_df], axis=1)

    posted_date_parsed = df.apply(
        lambda row: clean_posted_date(row["posted_date"], row["scraped_at"]),
        axis=1
    )
    posted_date_df = pd.DataFrame(posted_date_parsed.tolist())

    df = df.drop(columns=["salary", "location", "posted_date"])

    df = pd.concat([df, posted_date_df], axis=1)

    seniority_parsed = df["job_title"].apply(extract_seniority)
    seniority_df = pd.DataFrame(seniority_parsed.tolist())
    df = pd.concat([df, seniority_df], axis=1)

    df["processed_at"] = datetime.now().isoformat()

    return df

def save_parquet(df, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_parquet(path, index=False)
    print(f"Saved {len(df)} rows to {path}")

if __name__ == "__main__":
    df_raw = load_raw_data(RAW_DATA_PATH)
    df_clean = transform(df_raw)
    save_parquet(df_clean, OUTPUT_PATH)