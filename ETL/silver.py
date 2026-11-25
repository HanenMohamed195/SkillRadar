
import json
import re
import math
from urllib.parse import urlsplit, urlunsplit

from config import BRONZE_DATA, SILVER_DATA


# --------------------------------------------------
# MISSING VALUES
# --------------------------------------------------

MISSING_VALUES = {
    "",
    "nan",
    "none",
    "null",
    "n/a",
    "na",
    "not available",
    "not provided",
    "undefined"
}


# --------------------------------------------------
# LOAD BRONZE FILES
# --------------------------------------------------

def load_bronze_files():
    jobs = []

    files = [
        BRONZE_DATA / "latest_jobspy.json",
        BRONZE_DATA / "latest_remotive.json"
    ]

    for file_path in files:
        if not file_path.exists():
            print(f"File not found: {file_path}")
            continue

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            jobs.extend(data)

    return jobs


# --------------------------------------------------
# CLEAN TEXT
# --------------------------------------------------

def clean_text(value):
    if value is None:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    value = re.sub(r"\s+", " ", str(value)).strip()

    # Treat placeholder strings as missing values
    if value.casefold() in MISSING_VALUES:
        return None

    return value or None


# --------------------------------------------------
# NORMALIZE URL
# --------------------------------------------------

def normalize_url(url):
    url = clean_text(url)

    if not url:
        return None

    try:
        parts = urlsplit(url)

        # Preserve query parameters because they may contain
        # unique job IDs (such as Indeed's jk parameter).
        return urlunsplit((
            parts.scheme.lower(),
            parts.netloc.lower(),
            parts.path.rstrip("/"),
            parts.query,
            ""
        ))

    except ValueError:
        return url


# --------------------------------------------------
# CLEAN SKILLS
# --------------------------------------------------

def clean_skills(skills):
    if isinstance(skills, str):
        skills = re.split(r"[,;|]", skills)

    if not isinstance(skills, list):
        return []

    cleaned_skills = []
    seen = set()

    for skill in skills:
        skill = clean_text(skill)

        if not skill:
            continue

        key = skill.casefold()

        if key not in seen:
            seen.add(key)
            cleaned_skills.append(skill)

    return cleaned_skills


# --------------------------------------------------
# CLEAN JOB
# --------------------------------------------------

def clean_job(job):
    cleaned = {}

    for key, value in job.items():
        if isinstance(value, str):
            cleaned[key] = clean_text(value)
        else:
            cleaned[key] = value

    # Normalize URL
    cleaned["job_url"] = normalize_url(
        cleaned.get("job_url")
    )

    # Normalize skills
    cleaned["skills"] = clean_skills(
        cleaned.get("skills")
    )

    # Check whether description is genuinely available
    description = clean_text(
        cleaned.get("description")
    )

    cleaned["description"] = description

    cleaned["has_description"] = (
        isinstance(description, str)
        and bool(description.strip())
    )

    cleaned["data_quality"] = (
        "complete_for_skill_extraction"
        if cleaned["has_description"]
        else "missing_description"
    )

    return cleaned


# --------------------------------------------------
# DEDUPLICATION KEY
# --------------------------------------------------

def get_dedup_key(job):
    source = str(
        job.get("source") or ""
    ).strip().casefold()

    external_id = clean_text(
        job.get("external_id")
    )

    job_url = clean_text(
        job.get("job_url")
    )

    # Prefer external ID, scoped by source
    if external_id:
        return (
            source,
            "id",
            external_id.casefold()
        )

    # Fallback to URL, also scoped by source
    if job_url:
        return (
            source,
            "url",
            job_url.casefold()
        )

    return None


# --------------------------------------------------
# RUN SILVER LAYER
# --------------------------------------------------

def run_silver():
    bronze_jobs = load_bronze_files()

    silver_jobs = []
    seen = set()

    for job in bronze_jobs:
        if not isinstance(job, dict):
            continue

        cleaned = clean_job(job)

        # Keep records with a title.
        # Missing descriptions do not mean the job is invalid.
        if not cleaned.get("title"):
            continue

        key = get_dedup_key(cleaned)

        if key and key in seen:
            continue

        if key:
            seen.add(key)

        silver_jobs.append(cleaned)

    SILVER_DATA.mkdir(parents=True, exist_ok=True)

    output_file = SILVER_DATA / "silver_jobs.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            silver_jobs,
            file,
            ensure_ascii=False,
            indent=4,
            default=str
        )

    print("\nSilver Layer completed!")

    print(f"Bronze records: {len(bronze_jobs)}")
    print(f"Silver records: {len(silver_jobs)}")
    print(f"Removed: {len(bronze_jobs) - len(silver_jobs)}")

    print(f"Saved to: {output_file}")

    # Source breakdown
    source_counts = {}

    for job in silver_jobs:
        source = job.get("source") or "unknown"

        source_counts[source] = (
            source_counts.get(source, 0) + 1
        )

    print("\nSource breakdown:")

    for source, count in source_counts.items():
        print(f"{source}: {count}")

    # Description breakdown
    with_description = sum(
        1 for job in silver_jobs
        if job.get("has_description")
    )

    without_description = (
        len(silver_jobs) - with_description
    )

    print(
        f"\nJobs with descriptions: {with_description}"
    )

    print(
        f"Jobs without descriptions: {without_description}"
    )

    # Data quality breakdown
    quality_counts = {}

    for job in silver_jobs:
        quality = job.get("data_quality")

        quality_counts[quality] = (
            quality_counts.get(quality, 0) + 1
        )

    print("\nData quality breakdown:")

    for quality, count in quality_counts.items():
        print(f"{quality}: {count}")

    return silver_jobs


if __name__ == "__main__":
    run_silver()
