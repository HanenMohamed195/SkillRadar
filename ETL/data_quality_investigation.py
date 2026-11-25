import json
from collections import Counter
from pathlib import Path

from config import GOLD_DATA

JOBS_FILE = GOLD_DATA / "normalized_jobs.json"
REPORT_FILE = GOLD_DATA / "data_quality_investigation.json"


def load_jobs():
    with open(JOBS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def run_investigation():
    jobs = load_jobs()

    no_skills = [
        job for job in jobs
        if not job.get("normalized_skills")
    ]

    no_description = [
        job for job in jobs
        if not job.get("description")
        or not str(job.get("description")).strip()
    ]

    # Breakdown by source
    source_counts = Counter(
        job.get("source", "unknown")
        for job in jobs
    )

    no_skills_by_source = Counter(
        job.get("source", "unknown")
        for job in no_skills
    )

    no_description_by_source = Counter(
        job.get("source", "unknown")
        for job in no_description
    )

    # Description length analysis
    description_lengths = [
        len(str(job.get("description") or "").strip())
        for job in jobs
    ]

    descriptions_short = [
        job for job in jobs
        if len(str(job.get("description") or "").strip()) < 100
    ]

    no_skills_description_lengths = [
        len(str(job.get("description") or "").strip())
        for job in no_skills
    ]

    # Samples for manual inspection
    samples = []

    for job in no_skills[:25]:
        description = str(job.get("description") or "")

        samples.append({
            "job_id": job.get("job_id"),
            "source": job.get("source"),
            "title": job.get("title"),
            "company": job.get("company"),
            "description_length": len(description.strip()),
            "description_preview": description[:500],
            "job_url": job.get("job_url")
        })

    report = {
        "summary": {
            "total_jobs": len(jobs),
            "jobs_without_skills": len(no_skills),
            "jobs_with_skills": len(jobs) - len(no_skills),
            "jobs_without_descriptions": len(no_description),
            "descriptions_under_100_chars": len(descriptions_short),
            "average_description_length": (
                round(sum(description_lengths) / len(description_lengths), 2)
                if description_lengths else 0
            ),
            "average_description_length_without_skills": (
                round(
                    sum(no_skills_description_lengths)
                    / len(no_skills_description_lengths), 2
                )
                if no_skills_description_lengths else 0
            )
        },
        "source_distribution": dict(source_counts),
        "no_skills_by_source": dict(no_skills_by_source),
        "no_description_by_source": dict(no_description_by_source),
        "short_descriptions_by_source": dict(
            Counter(
                job.get("source", "unknown")
                for job in descriptions_short
            )
        ),
        "sample_jobs_without_skills": samples
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Console output
    print("\n" + "=" * 50)
    print(" SKILLRADAR DATA QUALITY INVESTIGATION")
    print("=" * 50)

    print("\n--- SUMMARY ---")
    for key, value in report["summary"].items():
        print(f"{key}: {value}")

    print("\n--- SOURCE DISTRIBUTION ---")
    for source, count in source_counts.items():
        print(f"{source}: {count}")

    print("\n--- JOBS WITHOUT SKILLS BY SOURCE ---")
    for source, count in no_skills_by_source.items():
        print(f"{source}: {count}")

    print("\n--- JOBS WITHOUT DESCRIPTIONS BY SOURCE ---")
    for source, count in no_description_by_source.items():
        print(f"{source}: {count}")

    print("\n--- DESCRIPTIONS UNDER 100 CHARS BY SOURCE ---")
    for source, count in report["short_descriptions_by_source"].items():
        print(f"{source}: {count}")

    print("\n--- SAMPLE JOBS WITHOUT SKILLS ---")
    for i, job in enumerate(samples, 1):
        print(f"\n{i}. {job['title']} | {job['source']}")
        print(f"Company: {job['company']}")
        print(f"Description length: {job['description_length']}")
        print(f"Preview: {job['description_preview'][:250]}")

    print(f"\nInvestigation report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    run_investigation()