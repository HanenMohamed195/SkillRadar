
import json
from datetime import datetime, timezone

from config import JOBSPY_FILE, REMOTIVE_FILE, BRONZE_DATA


def load_json(file_path):
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return []

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(data, file_path):
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4, default=str)


def run_bronze():
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    jobspy_jobs = load_json(JOBSPY_FILE)
    remotive_jobs = load_json(REMOTIVE_FILE)

    # حفظ نسخة خام مؤرخة لكل مصدر
    save_json(jobspy_jobs, BRONZE_DATA / f"jobspy_{timestamp}.json")
    save_json(remotive_jobs, BRONZE_DATA / f"remotive_{timestamp}.json")

    # حفظ أحدث نسخة منفصلة لاستخدامها في Silver
    save_json(jobspy_jobs, BRONZE_DATA / "latest_jobspy.json")
    save_json(remotive_jobs, BRONZE_DATA / "latest_remotive.json")

    print(f"Bronze JobSpy: {len(jobspy_jobs)}")
    print(f"Bronze Remotive: {len(remotive_jobs)}")
    print(f"Total Bronze: {len(jobspy_jobs) + len(remotive_jobs)}")

    return jobspy_jobs + remotive_jobs


if __name__ == "__main__":
    run_bronze()

