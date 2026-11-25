
from pipeline.transform import (
    clean_html,
    get_relevant_description,
    extract_skills
)


def test_clean_html():
    text = "<p>Hello <b>Python</b></p>"

    result = clean_html(text)

    assert result == "Hello Python"


def test_clean_html_empty():
    assert clean_html("") == ""


def test_clean_html_remove_extra_spaces():
    text = "Hello     Python"

    result = clean_html(text)

    assert result == "Hello Python"


def test_get_relevant_description():
    description = (
        "Welcome to our company. "
        "Requirements: Python and SQL. "
        "Not your tech stack? Check other jobs."
    )

    result = get_relevant_description(description)

    assert "python" in result
    assert "sql" in result
    assert "not your tech stack?" not in result


def test_extract_skills():
    skills_dictionary = {
        "Python": ["python"],
        "SQL": ["sql"],
        "Excel": ["microsoft excel"]
    }

    result = extract_skills(
        "Data Analyst",
        "We need experience with Python and SQL.",
        skills_dictionary
    )

    assert result == ["Python", "SQL"]


def test_extract_skills_from_title():
    skills_dictionary = {
        "Python": ["python"],
        "React": ["react"]
    }

    result = extract_skills(
        "Senior Python Developer",
        "We are looking for a developer.",
        skills_dictionary
    )

    assert "Python" in result
