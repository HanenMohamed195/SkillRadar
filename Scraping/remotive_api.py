
import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError

from normalize import normalize_job

API_URL = "https://remotive.com/api/remote-jobs"


def fetch_remotive_jobs(search=None):
    params = {}

    if search:
        params["search"] = search

    url = API_URL + "?" + urlencode(params)

    request = Request(
        url,
        headers={"User-Agent": "SkillRadar-Development/1.0"}
    )

    try:
        with urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))

        results = []

        for job in data.get("jobs", []):
            raw_job = {
                "external_id": job.get("id"),
                "title": job.get("title"),
                "company": job.get("company_name"),
                "description": job.get("description"),
                "location": job.get("candidate_required_location"),
                "salary": job.get("salary"),
                "job_type": job.get("job_type"),
                "category": job.get("category"),
                "skills": job.get("tags", []),
                "posted_date": job.get("publication_date"),
                "job_url": job.get("url")
            }

            results.append(normalize_job(raw_job, "Remotive"))

        return results

    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        print(f"Remotive error: {error}")
        return []


def save_remotive_jobs(jobs):
    output_dir = Path(__file__).parent / "data"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "remotive_jobs.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(jobs, file, ensure_ascii=False, indent=4)

    print(f"Remotive saved: {len(jobs)} jobs")
