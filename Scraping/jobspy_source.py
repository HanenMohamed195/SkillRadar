import math
import json
import time
import sys
from pathlib import Path

import pandas as pd
from jobspy import scrape_jobs

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize import normalize_job


SEARCH_TERMS = [
    "data analyst",
    "junior data analyst",
    "business analyst",
    "business intelligence analyst",
    "BI analyst",
    "BI developer",
    "Power BI developer",
    "reporting analyst",
    "SQL analyst",
    "SQL developer",
    "data scientist",
    "junior data scientist",
    "data engineer",
    "analytics engineer",
    "machine learning engineer",
    "AI engineer",
    "Python developer",
    "Python data analyst",
    "ETL developer",
    "database developer",
    "software engineer",
    "backend developer",
    "frontend developer",
    "full stack developer"
]

def clean_json_values(value):
    if isinstance(value, dict):
        return {
            key: clean_json_values(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [clean_json_values(item) for item in value]

    if isinstance(value, float) and not math.isfinite(value):
        return None

    return value

def fetch_jobs():
    all_jobs = []

    for term in SEARCH_TERMS:
        print(f"\nSearching for: {term}")

        try:
            jobs = scrape_jobs(
                site_name=["indeed", "bayt"],
                search_term=term,
                location="Egypt",
                results_wanted=100,
                country_indeed="Egypt",
                hours_old=2160,
                verbose=1
            )

            if jobs is not None and not jobs.empty:
                print(f"Found {len(jobs)} jobs for {term}")
                all_jobs.append(jobs)
            else:
                print(f"No jobs found for {term}")

        except Exception as error:
            print(f"Error searching {term}: {error}")

        # انتظار بسيط بين عمليات البحث
        time.sleep(5)

    if not all_jobs:
        return pd.DataFrame()

    combined = pd.concat(all_jobs, ignore_index=True)

    return combined


def save_jobs(df):
    if df is None or df.empty:
        print("No JobSpy jobs to save.")
        return

    output_dir = Path(__file__).resolve().parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    jobs_list = []

    for _, job in df.iterrows():
        job_dict = job.to_dict()

        normalized = normalize_job({
            "external_id": job_dict.get("id"),
            "title": job_dict.get("title"),
            "company": job_dict.get("company"),
            "description": job_dict.get("description"),
            "location": job_dict.get("location"),
            "salary": job_dict.get("min_amount"),
            "job_type": job_dict.get("job_type"),
            "category": job_dict.get("category"),
            "skills": job_dict.get("skills") or [],
            "posted_date": job_dict.get("date_posted"),
            "job_url": job_dict.get("job_url")
        }, source=job_dict.get("site") or "JobSpy")

        jobs_list.append(normalized)

    unique_jobs = {}

    for job in jobs_list:
        key = (
            str(job.get("source") or "").lower(),
            str(job.get("job_url") or "").lower()
        )

        if key[1]:
            unique_jobs[key] = job
        else:
            unique_jobs[(key[0], str(job.get("external_id") or ""))] = job

    final_jobs = list(unique_jobs.values())

    # Convert NaN and Infinity to valid JSON null values
    final_jobs = clean_json_values(final_jobs)
    output_file = output_dir / "jobspy_jobs.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            final_jobs,
            file,
            ensure_ascii=False,
            indent=4,
            default=str,
            allow_nan=False
    )

    print(f"\nTotal unique JobSpy jobs: {len(final_jobs)}")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    jobs_df = fetch_jobs()
    save_jobs(jobs_df)
