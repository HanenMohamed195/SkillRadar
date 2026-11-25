
from matching.matcher import calculate_match, rank_jobs


def test_calculate_match():
    user_skills = ["Python", "SQL"]
    job_skills = ["Python", "SQL", "AWS"]

    result = calculate_match(user_skills, job_skills)

    assert result["score"] == 66.67
    assert result["matched_skills"] == ["Python", "SQL"]
    assert result["missing_skills"] == ["AWS"]


def test_no_matching_skills():
    user_skills = ["HTML", "CSS"]
    job_skills = ["Python", "SQL"]

    result = calculate_match(user_skills, job_skills)

    assert result["score"] == 0
    assert result["matched_skills"] == []
    assert result["missing_skills"] == ["Python", "SQL"]


def test_empty_job_skills():
    result = calculate_match(["Python"], [])

    assert result["score"] is None
    assert result["matched_skills"] == []
    assert result["missing_skills"] == []


def test_case_insensitive_matching():
    result = calculate_match(
        ["python", "SQL"],
        ["Python", "sql"]
    )

    assert result["score"] == 100
    assert result["matched_skills"] == ["Python", "sql"]


def test_rank_jobs():
    jobs = [
        {"title": "Job A", "skills": ["Python", "SQL", "AWS"]},
        {"title": "Job B", "skills": ["Python", "SQL"]}
    ]

    results = rank_jobs(jobs, ["Python", "SQL"])

    assert results[0]["title"] == "Job B"
    assert results[0]["score"] == 100
    assert results[1]["score"] == 66.67
