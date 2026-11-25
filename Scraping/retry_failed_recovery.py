
import json
import time
import os
from pathlib import Path
from datetime import datetime, timezone

from description_recovery import recover_description

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "jobspy_jobs.json"
TEMP_FILE = BASE_DIR / "data" / "jobspy_jobs.tmp"

RETRY_STATUSES = {"http_502"}


def save_jobs(jobs):
    with open(TEMP_FILE, "w", encoding="utf-8") as file:
        json.dump(
            jobs,
            file,
            ensure_ascii=False,
            indent=4,
            allow_nan=False
        )

    os.replace(TEMP_FILE, INPUT_FILE)


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        jobs = json.load(file)

    retry_jobs = [
        job for job in jobs
        if job.get("description_recovery_status") == "failed"
        and job.get("description_recovery_error") in RETRY_STATUSES
    ]

    print(f"Jobs to retry: {len(retry_jobs)}")

    recovered = 0

    for number, job in enumerate(retry_jobs, start=1):
        print(f"\n[{number}/{len(retry_jobs)}] {job.get('title')}")

        description, status = recover_description(job.get("job_url"))

        job["description_recovery_attempted_at"] = (
            datetime.now(timezone.utc).isoformat()
        )

        if description:
            job["description"] = description
            job["description_recovery_status"] = "recovered"
            job["description_recovery_source"] = job.get("job_url")
            job.pop("description_recovery_error", None)
            recovered += 1
            print("Recovered successfully!")
        else:
            job["description_recovery_error"] = status
            print(f"Still not recovered: {status}")

        save_jobs(jobs)
        time.sleep(8)

    print("\n========== RETRY SUMMARY ==========")
    print(f"Retried: {len(retry_jobs)}")
    print(f"Recovered: {recovered}")
    print(f"Still failed: {len(retry_jobs) - recovered}")


if __name__ == "__main__":
    main()
