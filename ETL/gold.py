
import json
from collections import Counter

from config import SILVER_DATA, GOLD_DATA


def run_gold():
    input_file = SILVER_DATA / "silver_jobs.json"

    with open(input_file, "r", encoding="utf-8") as file:
        jobs = json.load(file)

    source_counts = Counter()
    title_counts = Counter()
    company_counts = Counter()
    skill_counts = Counter()

    for job in jobs:
        source_counts[job.get("source") or "Unknown"] += 1
        title_counts[job.get("title") or "Unknown"] += 1
        company_counts[job.get("company") or "Unknown"] += 1

        for skill in job.get("skills", []):
            if skill:
                skill_counts[str(skill).strip().lower()] += 1

    gold_data = {
        "total_jobs": len(jobs),
        "jobs_by_source": dict(source_counts.most_common()),
        "top_job_titles": dict(title_counts.most_common(10)),
        "top_companies": dict(company_counts.most_common(10)),
        "top_skills": dict(skill_counts.most_common(20))
    }

    GOLD_DATA.mkdir(parents=True, exist_ok=True)

    output_file = GOLD_DATA / "gold_summary.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            gold_data,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("Gold Layer completed!")
    print(f"Total jobs: {len(jobs)}")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    run_gold()

