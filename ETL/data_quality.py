import json
from collections import Counter
from pathlib import Path

from config import GOLD_DATA


JOBS_FILE = GOLD_DATA / "normalized_jobs.json"
DATASET_FILE = GOLD_DATA / "job_skill_dataset.json"
TAXONOMY_FILE = GOLD_DATA / "skill_taxonomy.json"

REPORT_FILE = GOLD_DATA / "data_quality_report.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_taxonomy_names(taxonomy):
    """Handle common taxonomy JSON structures."""
    if isinstance(taxonomy, dict):
        return set(taxonomy.keys())

    if isinstance(taxonomy, list):
        names = set()
        for item in taxonomy:
            if isinstance(item, str):
                names.add(item)
            elif isinstance(item, dict):
                name = (
                    item.get("canonical_name")
                    or item.get("name")
                    or item.get("skill")
                )
                if name:
                    names.add(name)
        return names

    return set()


def run_validation():
    jobs = load_json(JOBS_FILE)
    dataset = load_json(DATASET_FILE)
    taxonomy = load_json(TAXONOMY_FILE)

    taxonomy_names = get_taxonomy_names(taxonomy)

    checks = []
    errors = []
    warnings = []

    def add_check(name, status, details):
        checks.append({
            "check": name,
            "status": status,
            "details": details
        })

        if status == "FAIL":
            errors.append(name)
        elif status == "WARNING":
            warnings.append(name)

    # --------------------------------------------------
    # 1. Basic dataset checks
    # --------------------------------------------------

    add_check(
        "Jobs dataset is not empty",
        "PASS" if jobs else "FAIL",
        f"Total jobs: {len(jobs)}"
    )

    add_check(
        "Job-skill dataset is not empty",
        "PASS" if dataset else "FAIL",
        f"Total job-skill rows: {len(dataset)}"
    )

    add_check(
        "Skill taxonomy is not empty",
        "PASS" if taxonomy_names else "FAIL",
        f"Unique taxonomy skills: {len(taxonomy_names)}"
    )

    # --------------------------------------------------
    # 2. Job ID checks
    # --------------------------------------------------

    job_ids = [job.get("job_id") for job in jobs]
    missing_job_ids = [
        i for i, job_id in enumerate(job_ids)
        if not job_id
    ]

    duplicate_job_ids = [
        job_id for job_id, count in Counter(job_ids).items()
        if job_id and count > 1
    ]

    add_check(
        "Missing job IDs",
        "FAIL" if missing_job_ids else "PASS",
        f"Missing IDs: {len(missing_job_ids)}"
    )

    add_check(
        "Unique job IDs",
        "FAIL" if duplicate_job_ids else "PASS",
        f"Duplicate IDs: {len(duplicate_job_ids)}"
    )

    # --------------------------------------------------
    # 3. Required fields and job completeness
    # --------------------------------------------------

    required_fields = ["title", "company", "source", "job_url"]

    missing_fields = Counter()
    for job in jobs:
        for field in required_fields:
            if not job.get(field):
                missing_fields[field] += 1

    for field in required_fields:
        count = missing_fields[field]
        add_check(
            f"Required field: {field}",
            "WARNING" if count else "PASS",
            f"Missing/empty values: {count}"
        )

    # Descriptions are optional for some sources
    missing_descriptions = sum(
        1 for job in jobs
        if not job.get("description")
    )

    add_check(
        "Job descriptions",
        "WARNING" if missing_descriptions else "PASS",
        f"Jobs without descriptions: {missing_descriptions}"
    )

    # --------------------------------------------------
    # 4. Skills inside normalized jobs
    # --------------------------------------------------

    jobs_without_skills = sum(
        1 for job in jobs
        if not job.get("normalized_skills")
    )

    add_check(
        "Jobs with normalized skills",
        "WARNING" if jobs_without_skills else "PASS",
        f"Jobs without skills: {jobs_without_skills}"
    )

    skills_not_in_taxonomy = set()
    duplicate_skills_per_job = 0

    for job in jobs:
        skills = job.get("normalized_skills") or []

        if len(skills) != len(set(skills)):
            duplicate_skills_per_job += 1

        for skill in skills:
            if skill not in taxonomy_names:
                skills_not_in_taxonomy.add(skill)

    add_check(
        "Skills match taxonomy",
        "FAIL" if skills_not_in_taxonomy else "PASS",
        f"Skills not in taxonomy: {sorted(skills_not_in_taxonomy)}"
    )

    add_check(
        "Duplicate skills inside jobs",
        "FAIL" if duplicate_skills_per_job else "PASS",
        f"Jobs with duplicate skills: {duplicate_skills_per_job}"
    )

    # --------------------------------------------------
    # 5. Job-skill dataset validation
    # --------------------------------------------------

    job_id_set = set(job_ids)
    dataset_job_ids = [
        row.get("job_id") for row in dataset
    ]

    orphan_rows = sum(
        1 for row in dataset
        if row.get("job_id") not in job_id_set
    )

    missing_row_fields = Counter()
    for row in dataset:
        for field in ["job_id", "source", "skill", "category"]:
            if not row.get(field):
                missing_row_fields[field] += 1

    missing_dataset_fields = sum(missing_row_fields.values())

    add_check(
        "Job-skill foreign keys",
        "FAIL" if orphan_rows else "PASS",
        f"Rows referencing unknown jobs: {orphan_rows}"
    )

    add_check(
        "Job-skill required fields",
        "FAIL" if missing_dataset_fields else "PASS",
        f"Missing field values: {missing_dataset_fields}"
    )

    # Duplicate relationship rows
    relationship_keys = [
        (
            row.get("job_id"),
            row.get("skill")
        )
        for row in dataset
    ]

    duplicate_relationships = sum(
        count - 1
        for count in Counter(relationship_keys).values()
        if count > 1
    )

    add_check(
        "Unique job-skill relationships",
        "FAIL" if duplicate_relationships else "PASS",
        f"Duplicate relationship rows: {duplicate_relationships}"
    )

    dataset_skills_not_in_taxonomy = {
        row.get("skill")
        for row in dataset
        if row.get("skill") not in taxonomy_names
    }

    add_check(
        "Dataset skills match taxonomy",
        "FAIL" if dataset_skills_not_in_taxonomy else "PASS",
        f"Unknown skills: {sorted(dataset_skills_not_in_taxonomy)}"
    )

    # --------------------------------------------------
    # 6. Consistency between jobs and relationship dataset
    # --------------------------------------------------

    expected_relationships = set()

    for job in jobs:
        for skill in job.get("normalized_skills") or []:
            expected_relationships.add(
                (job.get("job_id"), skill)
            )

    actual_relationships = set(relationship_keys)

    missing_relationships = expected_relationships - actual_relationships
    extra_relationships = actual_relationships - expected_relationships

    add_check(
        "Jobs and job-skill dataset consistency",
        "FAIL" if missing_relationships or extra_relationships else "PASS",
        (
            f"Missing rows: {len(missing_relationships)}, "
            f"Extra rows: {len(extra_relationships)}"
        )
    )

    # --------------------------------------------------
    # 7. Source profiling
    # --------------------------------------------------

    source_counts = Counter(
        job.get("source", "unknown")
        for job in jobs
    )

    skill_counts = Counter(
        skill
        for job in jobs
        for skill in (job.get("normalized_skills") or [])
    )

    # Count jobs per skill, not individual mentions
    skill_job_counts = Counter()
    for job in jobs:
        for skill in set(job.get("normalized_skills") or []):
            skill_job_counts[skill] += 1

    # --------------------------------------------------
    # 8. Summary and report
    # --------------------------------------------------

    passed = sum(
        1 for check in checks
        if check["status"] == "PASS"
    )

    failed = sum(
        1 for check in checks
        if check["status"] == "FAIL"
    )

    warning_count = sum(
        1 for check in checks
        if check["status"] == "WARNING"
    )

    report = {
        "summary": {
            "total_jobs": len(jobs),
            "job_skill_rows": len(dataset),
            "taxonomy_skills": len(taxonomy_names),
            "passed_checks": passed,
            "failed_checks": failed,
            "warnings": warning_count,
            "overall_status": (
                "FAIL" if failed else
                "PASS_WITH_WARNINGS" if warning_count else
                "PASS"
            )
        },
        "checks": checks,
        "source_distribution": dict(source_counts),
        "top_20_skills": skill_job_counts.most_common(20),
        "missing_fields": dict(missing_fields),
        "jobs_without_descriptions": missing_descriptions,
        "jobs_without_skills": jobs_without_skills,
        "duplicate_job_ids": duplicate_job_ids,
        "skills_not_in_taxonomy": sorted(skills_not_in_taxonomy),
        "dataset_skills_not_in_taxonomy": sorted(
            dataset_skills_not_in_taxonomy
        ),
        "duplicate_relationships": duplicate_relationships,
        "orphan_rows": orphan_rows,
        "missing_relationships": len(missing_relationships),
        "extra_relationships": len(extra_relationships)
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # --------------------------------------------------
    # 9. Console output
    # --------------------------------------------------

    print("\n" + "=" * 50)
    print("       SKILLRADAR DATA QUALITY REPORT")
    print("=" * 50)

    print(f"Total jobs: {len(jobs)}")
    print(f"Job-skill rows: {len(dataset)}")
    print(f"Unique taxonomy skills: {len(taxonomy_names)}")

    print(f"\nPASS: {passed}")
    print(f"FAIL: {failed}")
    print(f"WARNING: {warning_count}")

    print("\n--- CHECK DETAILS ---")

    for check in checks:
        print(
            f"[{check['status']}] "
            f"{check['check']} - {check['details']}"
        )

    print("\n--- SOURCE DISTRIBUTION ---")
    for source, count in source_counts.items():
        print(f"{source}: {count}")

    print("\n--- TOP 20 SKILLS ---")
    for skill, count in skill_job_counts.most_common(20):
        print(f"{skill}: {count}")

    print("\n--- OVERALL STATUS ---")
    print(report["summary"]["overall_status"])

    print(f"\nReport saved to: {REPORT_FILE}")


if __name__ == "__main__":
    run_validation()