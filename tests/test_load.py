
import sqlite3

from pipeline import load


def create_test_job(source_id, title, skills=None):
    return {
        "source_id": source_id,
        "title": title,
        "company": "Test Company",
        "category": "Data",
        "job_type": "Full-time",
        "location_text": "Remote",
        "salary_text": None,
        "url": "https://example.com/job",
        "published_at": "2026-11-17",
        "description": "Test description",
        "skills": skills or []
    }


def get_connection(db_path):
    return sqlite3.connect(db_path)


def test_insert_job(monkeypatch, tmp_path):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(load, "DB_PATH", str(db_path))

    job = create_test_job(
        "101",
        "Python Developer",
        ["Python", "SQL"]
    )

    load.load_jobs([job])

    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT title FROM jobs")
    assert cursor.fetchone()[0] == "Python Developer"

    cursor.execute("SELECT skill FROM job_skills ORDER BY skill")
    assert [row[0] for row in cursor.fetchall()] == ["Python", "SQL"]

    conn.close()


def test_update_job(monkeypatch, tmp_path):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(load, "DB_PATH", str(db_path))

    first_job = create_test_job(
        "102",
        "Junior Developer",
        ["Python"]
    )

    load.load_jobs([first_job])

    updated_job = create_test_job(
        "102",
        "Senior Developer",
        ["SQL"]
    )

    load.load_jobs([updated_job])

    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT title FROM jobs WHERE source_id = ?", ("102",))
    assert cursor.fetchone()[0] == "Senior Developer"

    cursor.execute(
        "SELECT skill FROM job_skills WHERE source_id = ?",
        ("102",)
    )
    assert [row[0] for row in cursor.fetchall()] == ["SQL"]

    cursor.execute("SELECT inserted, updated FROM pipeline_runs ORDER BY run_id DESC")
    assert cursor.fetchone() == (0, 1)

    conn.close()


def test_skip_invalid_job(monkeypatch, tmp_path):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(load, "DB_PATH", str(db_path))

    valid_job = create_test_job("103", "Data Analyst")

    invalid_job = {
        "source_id": "104",
        "title": "",
        "url": "https://example.com/job"
    }

    load.load_jobs([valid_job, invalid_job])

    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM jobs")
    assert cursor.fetchone()[0] == 1

    cursor.execute(
        "SELECT retrieved, inserted, skipped_invalid, no_skills_found "
        "FROM pipeline_runs"
    )
    assert cursor.fetchone() == (2, 1, 1, 1)

    conn.close()
