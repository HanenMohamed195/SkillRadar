
import sqlite3
from datetime import datetime, timezone

from config import DB_PATH


def create_tables(conn):
    """Create the database tables."""

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            source_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            company TEXT,
            category TEXT,
            job_type TEXT,
            location_text TEXT,
            salary_text TEXT,
            url TEXT NOT NULL,
            published_at TEXT,
            description TEXT,
            last_seen_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_skills (
            source_id TEXT,
            skill TEXT,
            PRIMARY KEY (source_id, skill),
            FOREIGN KEY (source_id)
                REFERENCES jobs(source_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT,
            status TEXT,
            retrieved INTEGER,
            inserted INTEGER,
            updated INTEGER,
            skipped_invalid INTEGER,
            no_skills_found INTEGER,
            error_message TEXT
        )
    """)

    conn.commit()


def load_jobs(jobs):
    """Load cleaned jobs into SQLite."""

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    started_at = datetime.now(timezone.utc).isoformat()

    inserted = 0
    updated = 0
    skipped = 0
    no_skills = 0

    try:
        create_tables(conn)
        cursor = conn.cursor()

        for job in jobs:

            if not job.get("source_id") or not job.get("title") or not job.get("url"):
                skipped += 1
                continue

            cursor.execute(
                "SELECT source_id FROM jobs WHERE source_id = ?",
                (job["source_id"],)
            )

            exists = cursor.fetchone() is not None

            cursor.execute("""
                INSERT INTO jobs (
                    source_id, title, company, category,
                    job_type, location_text, salary_text,
                    url, published_at, description, last_seen_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_id) DO UPDATE SET
                    title = excluded.title,
                    company = excluded.company,
                    category = excluded.category,
                    job_type = excluded.job_type,
                    location_text = excluded.location_text,
                    salary_text = excluded.salary_text,
                    url = excluded.url,
                    published_at = excluded.published_at,
                    description = excluded.description,
                    last_seen_at = excluded.last_seen_at
            """, (
                job["source_id"],
                job["title"],
                job.get("company"),
                job.get("category"),
                job.get("job_type"),
                job.get("location_text"),
                job.get("salary_text"),
                job["url"],
                job.get("published_at"),
                job.get("description"),
                started_at
            ))

            if exists:
                updated += 1
            else:
                inserted += 1

            # Replace old skills with the latest extracted skills
            cursor.execute(
                "DELETE FROM job_skills WHERE source_id = ?",
                (job["source_id"],)
            )

            skills = job.get("skills", [])

            if not skills:
                no_skills += 1

            for skill in skills:
                cursor.execute("""
                    INSERT OR IGNORE INTO job_skills (source_id, skill)
                    VALUES (?, ?)
                """, (job["source_id"], skill))

        cursor.execute("""
            INSERT INTO pipeline_runs (
                started_at, status, retrieved, inserted,
                updated, skipped_invalid, no_skills_found,
                error_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            started_at, "success", len(jobs), inserted,
            updated, skipped, no_skills, None
        ))

        conn.commit()

        print("Database loading completed successfully!")
        print(f"Retrieved: {len(jobs)}")
        print(f"Inserted: {inserted}")
        print(f"Updated: {updated}")
        print(f"Skipped: {skipped}")
        print(f"Jobs without skills: {no_skills}")

    except Exception as error:
        conn.rollback()

        cursor.execute("""
            INSERT INTO pipeline_runs (
                started_at, status, retrieved, inserted,
                updated, skipped_invalid, no_skills_found,
                error_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            started_at, "failed", len(jobs), inserted,
            updated, skipped, no_skills, str(error)
        ))

        conn.commit()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    from pipeline.transform import transform_jobs

    cleaned_jobs = transform_jobs()
    load_jobs(cleaned_jobs)
