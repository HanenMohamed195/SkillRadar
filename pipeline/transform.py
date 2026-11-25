import json
import re
import html
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

RAW_FILE = DATA_DIR / "sample_jobs.json"
SKILLS_FILE = DATA_DIR / "skills.csv"


def clean_html(text):
    if not text:
        return ""

    text = html.unescape(str(text))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def load_skills():
    skills_df = pd.read_csv(SKILLS_FILE)

    skills_dictionary = {}

    for _, row in skills_df.iterrows():
        skill = str(row["skill"]).strip()

        aliases_value = row.get("aliases", "")

        if pd.isna(aliases_value):
            aliases_value = ""

        aliases = [
            alias.strip()
            for alias in str(aliases_value).split(",")
            if alias.strip()
        ]

        skills_dictionary[skill] = aliases

    return skills_dictionary


def get_relevant_description(description):
    text = description.lower()

    # Remove promotional sections first
    end_markers = [
        "not your tech stack?",
        "other opportunities",
        "check out our other jobs",
        "reach out and we'll match you"
    ]

    for marker in end_markers:
        position = text.find(marker)

        if position != -1:
            text = text[:position]

    # Find the beginning of the requirements section
    start_markers = [
        "who we're looking for",
        "who we are looking for",
        "what we're looking for",
        "what you'll need",
        "what you bring",
        "qualifications",
        "requirements"
    ]

    positions = []

    for marker in start_markers:
        position = text.find(marker)

        if position != -1:
            positions.append(position)

    if positions:
        text = text[min(positions):]

    return text


def extract_skills(title, description, skills_dictionary):
    title = str(title).lower()

    relevant_description = get_relevant_description(description)

    found_skills = []

    is_data_engineer = "data engineer" in title

    for skill, aliases in skills_dictionary.items():

        # Avoid detecting React in Data Engineer jobs
        if skill == "React" and is_data_engineer:
            continue

        keywords = [skill.lower()] + [
            alias.lower() for alias in aliases
        ]

        for keyword in keywords:

            if len(keyword) < 3:
                continue

            pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"

            if re.search(pattern, title):
                found_skills.append(skill)
                break

            if re.search(pattern, relevant_description):
                found_skills.append(skill)
                break

    return sorted(set(found_skills))


def transform_jobs():

    with open(RAW_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, list):
        jobs = data
    else:
        jobs = data.get("jobs", [])

    skills_dictionary = load_skills()

    cleaned_jobs = []

    for job in jobs:

        source_id = job.get("id")
        title = job.get("title")
        url = job.get("url")

        if not source_id or not title or not url:
            continue

        description = clean_html(job.get("description", ""))

        # We intentionally do not use job tags
        # because they may contain unrelated skills
        skills = extract_skills(
            title,
            description,
            skills_dictionary
        )

        cleaned_job = {
            "source_id": str(source_id),
            "title": title.strip(),
            "company": job.get("company_name"),
            "category": job.get("category"),
            "job_type": job.get("job_type"),
            "location_text": job.get("candidate_required_location"),
            "salary_text": job.get("salary"),
            "url": url,
            "published_at": job.get("publication_date"),
            "description": description,
            "skills": skills
        }

        cleaned_jobs.append(cleaned_job)

    return cleaned_jobs


if __name__ == "__main__":

    results = transform_jobs()

    print(f"Total cleaned jobs: {len(results)}")

    for job in results[:10]:

        print("\nJob:", job["title"])
        print("Skills:", job["skills"])
