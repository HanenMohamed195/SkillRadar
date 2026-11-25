
import sqlite3
from config import DB_PATH


def get_connection():
    """Connect to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_total_jobs():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM jobs")
        return cursor.fetchone()[0]
    finally:
        conn.close()


def get_jobs_by_category():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COALESCE(NULLIF(TRIM(category), ''), 'Other') AS category,
                COUNT(*) AS job_count
            FROM jobs
            GROUP BY category
            ORDER BY job_count DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_top_skills(limit=10):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                skill,
                COUNT(DISTINCT source_id) AS job_count
            FROM job_skills
            GROUP BY skill
            ORDER BY job_count DESC, skill ASC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_jobs_by_type():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COALESCE(NULLIF(TRIM(job_type), ''), 'Not specified') AS job_type,
                COUNT(*) AS job_count
            FROM jobs
            GROUP BY job_type
            ORDER BY job_count DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_recent_jobs(limit=10):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                title,
                company,
                category,
                published_at,
                url
            FROM jobs
            ORDER BY published_at DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_data_quality_summary():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COUNT(*) AS total_jobs,
                SUM(CASE WHEN title IS NULL OR TRIM(title) = ''
                    THEN 1 ELSE 0 END) AS missing_titles,
                SUM(CASE WHEN company IS NULL OR TRIM(company) = ''
                    THEN 1 ELSE 0 END) AS missing_companies,
                SUM(CASE WHEN category IS NULL OR TRIM(category) = ''
                    THEN 1 ELSE 0 END) AS missing_categories,
                SUM(CASE WHEN url IS NULL OR TRIM(url) = ''
                    THEN 1 ELSE 0 END) AS missing_urls
            FROM jobs
        """)
        return dict(cursor.fetchone())
    finally:
        conn.close()


def get_jobs_skills_summary():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COUNT(*) AS total_jobs,
                SUM(CASE WHEN skill_count > 0
                    THEN 1 ELSE 0 END) AS jobs_with_skills,
                SUM(CASE WHEN skill_count = 0
                    THEN 1 ELSE 0 END) AS jobs_without_skills
            FROM (
                SELECT
                    jobs.source_id,
                    COUNT(job_skills.skill) AS skill_count
                FROM jobs
                LEFT JOIN job_skills
                    ON jobs.source_id = job_skills.source_id
                GROUP BY jobs.source_id
            )
        """)
        return dict(cursor.fetchone())
    finally:
        conn.close()


def get_pipeline_history(limit=10):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                run_id,
                started_at,
                status,
                retrieved,
                inserted,
                updated,
                skipped_invalid,
                no_skills_found,
                error_message
            FROM pipeline_runs
            ORDER BY run_id DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
