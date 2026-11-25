
import json
from pathlib import Path

file_path = (
    Path(__file__).resolve().parent
    / "data"
    / "jobspy_jobs.json"
)

with open(file_path, "r", encoding="utf-8") as file:
    jobs = json.load(file)

failed_jobs = [
    job for job in jobs
    if job.get("source", "").lower() == "bayt"
    and job.get("description_recovery_status") == "failed"
]

print(f"Failed jobs: {len(failed_jobs)}")

for index, job in enumerate(failed_jobs, start=1):
    print(f"\n--- Job {index} ---")
    print("Title:", job.get("title"))
    print("Company:", job.get("company"))
    print("URL:", job.get("job_url"))
    print("Error:", job.get("description_recovery_error"))
