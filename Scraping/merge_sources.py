
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def load_jobs(filename):
    file_path = DATA_DIR / filename

    if not file_path.exists():
        print(f"File not found: {filename}")
        return []

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def merge_jobs():
    jobspy_jobs = load_jobs("jobspy_jobs.json")
    remotive_jobs = load_jobs("remotive_jobs.json")

    all_jobs = jobspy_jobs + remotive_jobs

    unique_jobs = {}
    for job in all_jobs:
        url = job.get("job_url")

        if url:
            unique_jobs[url] = job

    merged_jobs = list(unique_jobs.values())

    output_file = DATA_DIR / "all_jobs.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            merged_jobs,
            file,
            ensure_ascii=False,
            indent=4
        )

    print(f"JobSpy: {len(jobspy_jobs)}")
    print(f"Remotive: {len(remotive_jobs)}")
    print(f"Total unique jobs: {len(merged_jobs)}")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    merge_jobs()
