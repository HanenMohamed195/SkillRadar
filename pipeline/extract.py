
import requests
import json

from config import API_URL, SAMPLE_LIMIT, DATA_DIR


def fetch_jobs(limit=SAMPLE_LIMIT):

    response = requests.get(
        API_URL,
        params={"limit": limit},
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    jobs = data.get("jobs", [])

    if not isinstance(jobs, list):
        raise ValueError("Invalid API response")

    return jobs


def save_sample(jobs):

    DATA_DIR.mkdir(exist_ok=True)

    file_path = DATA_DIR / "sample_jobs.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(jobs, file, ensure_ascii=False, indent=4)

    print(f"Saved {len(jobs)} jobs successfully!")


if __name__ == "__main__":

    try:
        jobs = fetch_jobs()
        save_sample(jobs)

    except requests.RequestException as error:
        print("API Error:", error)
