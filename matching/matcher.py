
import sqlite3

from config import DB_PATH


def calculate_match(user_skills, job_skills):
    """Calculate skill overlap and missing skills."""

    user_map = {
        skill.strip().casefold(): skill.strip()
        for skill in user_skills
        if skill and skill.strip()
    }

    job_map = {
        skill.strip().casefold(): skill.strip()
        for skill in job_skills
        if skill and skill.strip()
    }

    if not job_map:
        return {
            "score": None,
            "matched_skills": [],
            "missing_skills": []
        }

    matched = [
        skill for key, skill in job_map.items()
        if key in user_map
    ]

    missing = [
        skill for key, skill in job_map.items()
        if key not in user_map
    ]

    score = len(matched) / len(job_map) * 100

    return {
        "score": round(score, 2),
        "matched_skills": matched,
        "missing_skills": missing
    }


def rank_jobs(jobs, user_skills):
    """Rank jobs by matching score."""

    ranked_jobs = []

    for job in jobs:
        result = calculate_match(
            user_skills,
            job.get("skills", [])
        )

        ranked_job = job.copy()
        ranked_job.update(result)

        ranked_jobs.append(ranked_job)

    ranked_jobs.sort(
        key=lambda job: (
            job["score"] is not None,
            job["score"] if job["score"] is not None else 0,
            len(job["matched_skills"]),
            job.get("published_at") or ""
        ),
        reverse=True
    )

    return ranked_jobs


def get_ranked_jobs(user_skills):
    """Read jobs from SQLite and rank them."""

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM jobs")
        rows = cursor.fetchall()

        jobs = [dict(row) for row in rows]

        cursor.execute("""
            SELECT source_id, skill
            FROM job_skills
        """)

        skills_rows = cursor.fetchall()

        skills_by_job = {}

        for row in skills_rows:
            skills_by_job.setdefault(
                row["source_id"], []
            ).append(row["skill"])

        for job in jobs:
            job["skills"] = skills_by_job.get(
                job["source_id"], []
            )

        return rank_jobs(jobs, user_skills)

    finally:
        conn.close()


if __name__ == "__main__":

    user_skills = ["Python", "SQL"]

    results = get_ranked_jobs(user_skills)

    print(f"\nTotal jobs found: {len(results)}")

    for job in results[:5]:
        print("\nJob:", job["title"])
        print("Company:", job["company"])
        print("Score:", job["score"])
        print("Matched:", job["matched_skills"])
        print("Missing:", job["missing_skills"])
