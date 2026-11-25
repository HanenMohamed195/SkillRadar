
import json
from collections import Counter

from config import GOLD_DATA
from skill_extraction import SKILL_DICTIONARY


# --------------------------------------------------
# SKILL CATEGORIES
# Every extracted skill gets a category.
# New skills without a category are marked Uncategorized.
# --------------------------------------------------

SKILL_CATEGORIES = {
    # Programming
    "Python": "Programming",
    "R": "Programming",
    "Java": "Programming",
    "JavaScript": "Programming",
    "TypeScript": "Programming",
    "C++": "Programming",
    "C#": "Programming",
    "PHP": "Programming",
    "HTML": "Web Development",
    "CSS": "Web Development",

    # Frontend and Backend
    "React": "Frontend Development",
    "Node.js": "Backend Development",
    "REST API": "Backend Development",
    "FastAPI": "Backend Development",
    "Flask": "Backend Development",
    "Django": "Backend Development",

    # Databases
    "SQL": "Databases",
    "SQL Server": "Databases",
    "MySQL": "Databases",
    "PostgreSQL": "Databases",
    "Oracle": "Databases",
    "MongoDB": "Databases",
    "SQLite": "Databases",
    "Redis": "Databases",
    "Snowflake": "Databases",
    "BigQuery": "Databases",
    "Redshift": "Databases",

    # Data Analytics
    "Excel": "Data Analytics",
    "Power Query": "Data Analytics",
    "Statistics": "Data Analytics",
    "Data Analysis": "Data Analytics",
    "Data Cleaning": "Data Analytics",
    "Data Wrangling": "Data Analytics",

    # BI and Visualization
    "Power BI": "BI & Visualization",
    "Tableau": "BI & Visualization",
    "Looker": "BI & Visualization",
    "Looker Studio": "BI & Visualization",
    "DAX": "BI & Visualization",
    "Data Visualization": "BI & Visualization",
    "Business Intelligence": "BI & Visualization",
    "Reporting": "BI & Visualization",
    "Dashboard": "BI & Visualization",
    "Financial Reporting": "Finance",

    # AI and Machine Learning
    "Machine Learning": "AI & Machine Learning",
    "Deep Learning": "AI & Machine Learning",
    "Artificial Intelligence": "AI & Machine Learning",
    "NLP": "AI & Machine Learning",
    "Computer Vision": "AI & Machine Learning",
    "TensorFlow": "AI & Machine Learning",
    "PyTorch": "AI & Machine Learning",
    "Scikit-learn": "AI & Machine Learning",
    "Keras": "AI & Machine Learning",

    # Data Engineering
    "ETL": "Data Engineering",
    "ELT": "Data Engineering",
    "Data Engineering": "Data Engineering",
    "Data Pipelines": "Data Engineering",
    "Apache Spark": "Data Engineering",
    "Hadoop": "Data Engineering",
    "Airflow": "Data Engineering",
    "dbt": "Data Engineering",
    "Kafka": "Data Engineering",
    "Databricks": "Data Engineering",
    "Azure Data Factory": "Data Engineering",
    "Data Modeling": "Data Engineering",
    "Database Design": "Databases",

    # Cloud
    "Azure": "Cloud",
    "AWS": "Cloud",
    "Google Cloud": "Cloud",

    # DevOps and Version Control
    "Docker": "DevOps",
    "Kubernetes": "DevOps",
    "Git": "Version Control",
    "GitHub": "Version Control",
    "Linux": "Operating Systems",

    # Project Management
    "Agile": "Project Management",
    "Scrum": "Project Management",
    "Project Management": "Project Management",

    # Business Analysis
    "Business Analysis": "Business",
    "Requirements Analysis": "Business",
    "Business Requirements": "Business",
    "Requirements Management": "Business",
    "Stakeholder Management": "Business",
    "Process Analysis": "Business",
    "Process Mapping": "Business",
    "Change Management": "Business",
    "Gap Analysis": "Business",
    "Use Case Analysis": "Business",
    "Problem Solving": "Soft Skills",
    "Communication": "Soft Skills",

    # Enterprise Platforms
    "ServiceNow": "Enterprise Platforms",
    "SAP": "Enterprise Platforms",
    "SAP SD": "Enterprise Platforms",
    "Salesforce": "Enterprise Platforms",

    # Quality
    "Quality Assurance": "Quality Management",

    # Finance
    "Financial Analysis": "Finance",
    "Financial Modeling": "Finance",
    "Financial Planning": "Finance",
    "Forecasting": "Finance",
    "Budgeting": "Finance",
    "Treasury Management": "Finance",
    "Cash Flow Management": "Finance",
    "Risk Management": "Finance",
    "Investment Banking": "Finance",
    "Corporate Finance": "Finance",
    "Working Capital Management": "Finance",

    # Supply Chain and Operations
    "Supply Chain Management": "Supply Chain",
    "Demand Planning": "Supply Chain",
    "Inventory Management": "Supply Chain",
    "Procurement": "Supply Chain",
    "Operations Management": "Operations",

    # Business and Compliance
    "Revenue Management": "Business",
    "Compliance": "Compliance & Security",
    "Sustainability": "Business",
    "Cybersecurity": "Compliance & Security",
    "Information Security": "Compliance & Security",
    "Data Privacy": "Compliance & Security",

    # Other Professional Skills
    "Training": "Professional Skills",
    "Market Research": "Business",
    "Strategic Planning": "Business",
    "Client Relationship Management": "Business",
    "VBA": "Programming",
}


# --------------------------------------------------
# BUILD TAXONOMY AUTOMATICALLY
# Uses the exact same skills and aliases as Extraction.
# --------------------------------------------------

SKILL_TAXONOMY = {
    canonical_name: {
        "category": SKILL_CATEGORIES.get(
            canonical_name,
            "Uncategorized"
        ),
        "aliases": aliases
    }
    for canonical_name, aliases in SKILL_DICTIONARY.items()
}


# --------------------------------------------------
# LOAD EXTRACTION RESULTS
# --------------------------------------------------

def load_jobs():

    input_file = GOLD_DATA / "jobs_with_skills.json"

    if not input_file.exists():
        raise FileNotFoundError(
            f"Extraction file not found: {input_file}"
        )

    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            "Extraction data must be a JSON list."
        )

    return data


# --------------------------------------------------
# NORMALIZE SKILL
# --------------------------------------------------

def normalize_skill(skill):

    if not isinstance(skill, str):
        return None

    skill = skill.strip().casefold()

    if not skill:
        return None

    for canonical_name, details in SKILL_TAXONOMY.items():

        if skill == canonical_name.casefold():
            return canonical_name

        aliases = details["aliases"]

        for alias in aliases:

            if isinstance(alias, str) and skill == alias.strip().casefold():
                return canonical_name

    return None


# --------------------------------------------------
# GET SKILL CATEGORY
# --------------------------------------------------

def get_skill_category(skill):

    details = SKILL_TAXONOMY.get(skill)

    if details:
        return details["category"]

    return "Uncategorized"


# --------------------------------------------------
# PROCESS JOBS
# --------------------------------------------------

def run_normalization():

    jobs = load_jobs()

    normalized_jobs = []
    job_skill_rows = []

    skill_frequency = Counter()
    unmapped_skill_counter = Counter()
    category_frequency = Counter()

    jobs_with_skills = 0
    jobs_without_skills = 0

    for index, job in enumerate(jobs, start=1):

        if not isinstance(job, dict):
            print(f"Warning: Invalid job record at index {index}")
            continue

        # ------------------------------------------
        # Generate Job ID
        # ------------------------------------------

        external_id = job.get("external_id")
        source = job.get("source") or "unknown"

        if external_id:
            job_id = f"{source}_{external_id}"
        else:
            job_id = f"job_{index:06d}"

        # ------------------------------------------
        # Normalize Extracted Skills
        # ------------------------------------------

        raw_skills = job.get("extracted_skills", [])

        if not isinstance(raw_skills, list):
            raw_skills = []

        normalized_skills = set()

        for skill in raw_skills:

            normalized = normalize_skill(skill)

            if normalized:
                normalized_skills.add(normalized)
            elif skill:
                unmapped_skill_counter.update([str(skill)])

        normalized_skills = sorted(normalized_skills)

        # ------------------------------------------
        # Update Job Record
        # ------------------------------------------

        job["job_id"] = job_id
        job["normalized_skills"] = normalized_skills

        normalized_jobs.append(job)

        if normalized_skills:
            jobs_with_skills += 1
        else:
            jobs_without_skills += 1

        # ------------------------------------------
        # Create Job-Skill Relationships
        # ------------------------------------------

        for skill in normalized_skills:

            category = get_skill_category(skill)

            job_skill_rows.append({
                "job_id": job_id,
                "source": source,
                "skill": skill,
                "category": category
            })

            skill_frequency[skill] += 1
            category_frequency[category] += 1

    # --------------------------------------------------
    # PREPARE OUTPUT DIRECTORY
    # --------------------------------------------------

    GOLD_DATA.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------
    # SAVE NORMALIZED JOBS
    # --------------------------------------------------

    normalized_jobs_file = GOLD_DATA / "normalized_jobs.json"

    with open(normalized_jobs_file, "w", encoding="utf-8") as file:

        json.dump(
            normalized_jobs,
            file,
            ensure_ascii=False,
            indent=4,
            allow_nan=False
        )

    # --------------------------------------------------
    # SAVE JOB-SKILL DATASET
    # --------------------------------------------------

    job_skill_file = GOLD_DATA / "job_skill_dataset.json"

    with open(job_skill_file, "w", encoding="utf-8") as file:

        json.dump(
            job_skill_rows,
            file,
            ensure_ascii=False,
            indent=4,
            allow_nan=False
        )

    # --------------------------------------------------
    # SAVE SKILL TAXONOMY
    # --------------------------------------------------

    taxonomy_rows = []

    for skill, details in SKILL_TAXONOMY.items():

        taxonomy_rows.append({
            "skill": skill,
            "category": details["category"],
            "aliases": details["aliases"]
        })

    taxonomy_file = GOLD_DATA / "skill_taxonomy.json"

    with open(taxonomy_file, "w", encoding="utf-8") as file:

        json.dump(
            taxonomy_rows,
            file,
            ensure_ascii=False,
            indent=4,
            allow_nan=False
        )

    # --------------------------------------------------
    # SAVE NORMALIZATION SUMMARY
    # --------------------------------------------------

    summary = {
        "total_jobs": len(normalized_jobs),
        "jobs_with_skills": jobs_with_skills,
        "jobs_without_skills": jobs_without_skills,
        "total_job_skill_rows": len(job_skill_rows),
        "unique_normalized_skills": len(skill_frequency),
        "skills_frequency": dict(
            skill_frequency.most_common()
        ),
        "categories_frequency": dict(
            category_frequency.most_common()
        ),
        "taxonomy_skills_count": len(SKILL_TAXONOMY),
        "unmapped_skills_count": len(unmapped_skill_counter),
        "unmapped_skills": dict(
            unmapped_skill_counter.most_common()
        )
    }

    summary_file = GOLD_DATA / "normalized_skill_summary.json"

    with open(summary_file, "w", encoding="utf-8") as file:

        json.dump(
            summary,
            file,
            ensure_ascii=False,
            indent=4,
            allow_nan=False
        )

    # --------------------------------------------------
    # PRINT RESULTS
    # --------------------------------------------------

    print("\nSkill Normalization completed!")
    print("=" * 50)

    print(f"Total jobs: {len(normalized_jobs)}")
    print(f"Jobs with skills: {jobs_with_skills}")
    print(f"Jobs without skills: {jobs_without_skills}")

    print(f"Job-skill rows: {len(job_skill_rows)}")

    print(
        f"Unique normalized skills: "
        f"{len(skill_frequency)}"
    )

    print(
        f"Total taxonomy skills: "
        f"{len(SKILL_TAXONOMY)}"
    )

    print("\nTop 20 normalized skills:")

    for skill, count in skill_frequency.most_common(20):
        print(f"{skill}: {count}")

    # ------------------------------------------
    # Show Unmapped Skills
    # ------------------------------------------

    print("\nUnmapped skills:")

    if unmapped_skill_counter:

        for skill, count in unmapped_skill_counter.most_common():
            print(f"{skill}: {count}")

    else:
        print("None")

    # ------------------------------------------
    # Show Uncategorized Skills
    # ------------------------------------------

    uncategorized = [
        skill
        for skill, details in SKILL_TAXONOMY.items()
        if details["category"] == "Uncategorized"
    ]

    print("\nUncategorized taxonomy skills:")

    if uncategorized:
        for skill in uncategorized:
            print(skill)
    else:
        print("None")

    # ------------------------------------------
    # Output Paths
    # ------------------------------------------

    print("\nOutput files:")
    print(f"Normalized jobs: {normalized_jobs_file}")
    print(f"Job-skill dataset: {job_skill_file}")
    print(f"Skill taxonomy: {taxonomy_file}")
    print(f"Summary: {summary_file}")

    return normalized_jobs, job_skill_rows


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":
    run_normalization()
