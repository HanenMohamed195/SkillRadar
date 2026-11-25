
import json
import re
from collections import Counter

from config import SILVER_DATA, GOLD_DATA


# --------------------------------------------------
# SKILL DICTIONARY
# Canonical skill: accepted aliases
# --------------------------------------------------

SKILL_DICTIONARY = {
    # Data Analysis and BI
    "Python": ["python"],
    "SQL": ["sql"],
    "Excel": ["excel", "microsoft excel"],
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "Looker": ["looker"],
    "Looker Studio": ["looker studio", "google data studio"],
    "Power Query": ["power query"],
    "DAX": ["dax"],
    "VBA": ["vba"],
    "R": ["r programming", "r language", "rstudio"],
    "Statistics": ["statistics", "statistical analysis"],
    "Data Analysis": ["data analysis", "data analytics"],
    "Data Visualization": [
        "data visualization",
        "data visualisation"
    ],
    "Business Intelligence": [
        "business intelligence",
        "bi reporting"
    ],
    "Reporting": ["reporting", "report generation"],
    "Dashboard": ["dashboard", "dashboards"],

    # AI and Machine Learning
    "Machine Learning": ["machine learning"],
    "Deep Learning": ["deep learning"],
    "Artificial Intelligence": [
        "artificial intelligence",
        "ai",
        "ai/ml",
        "machine intelligence"
    ],
    "NLP": ["natural language processing", "nlp"],
    "Computer Vision": ["computer vision"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "Scikit-learn": [
        "scikit-learn",
        "scikit learn",
        "sklearn"
    ],
    "Keras": ["keras"],

    # Data Engineering
    "Data Cleaning": ["data cleaning", "data cleansing"],
    "Data Wrangling": ["data wrangling"],
    "ETL": ["etl"],
    "ELT": ["elt"],
    "Data Engineering": ["data engineering"],
    "Data Pipelines": ["data pipeline", "data pipelines"],
    "Apache Spark": ["apache spark", "pyspark"],
    "Hadoop": ["hadoop"],
    "Airflow": ["airflow", "apache airflow"],
    "dbt": ["dbt"],
    "Kafka": ["kafka"],
    "Databricks": ["databricks"],
    "Snowflake": ["snowflake"],
    "BigQuery": ["bigquery", "google bigquery"],
    "Redshift": ["redshift", "amazon redshift"],

    # Cloud
    "Azure": ["azure"],
    "AWS": ["aws", "amazon web services"],
    "Google Cloud": ["google cloud", "gcp"],
    "Azure Data Factory": ["azure data factory"],

    # DevOps and Tools
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes"],
    "Git": ["git"],
    "GitHub": ["github"],
    "Linux": ["linux"],

    # APIs and Frameworks
    "REST API": ["rest api", "restful api"],
    "FastAPI": ["fastapi"],
    "Flask": ["flask"],
    "Django": ["django"],

    # Programming
    "Java": ["java"],
    "JavaScript": ["javascript", "java script"],
    "TypeScript": ["typescript", "type script"],
    "C++": ["c++"],
    "C#": ["c#"],
    "HTML": ["html"],
    "CSS": ["css"],
    "React": ["react"],
    "Node.js": ["node.js", "nodejs", "node js"],
    "PHP": ["php"],

    # Databases
    "SQL Server": ["sql server", "microsoft sql server"],
    "MySQL": ["mysql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "Oracle": ["oracle database", "oracle sql"],
    "MongoDB": ["mongodb"],
    "SQLite": ["sqlite"],
    "Redis": ["redis"],

    # Database Design
    "Data Modeling": ["data modeling", "data modelling"],
    "Database Design": ["database design"],

    # Business Analysis and Management
    "Agile": ["agile"],
    "Scrum": ["scrum"],
    "Project Management": [
        "project management",
        "project planning",
        "project coordination"
    ],
    "Business Analysis": ["business analysis"],
    "Requirements Analysis": ["requirements analysis"],
    "Problem Solving": ["problem solving"],
    "Communication": [
        "communication skills",
        "strong communication",
        "verbal communication",
        "written communication",
        "communication"
    ],

    # Enterprise Platforms
    "ServiceNow": ["servicenow", "service now"],
    "SAP": ["sap"],
    "SAP SD": [
        "sap sd",
        "sap sales and distribution",
        "sales and distribution"
    ],
    "Salesforce": ["salesforce"],

    # Business Analysis Skills
    "Business Requirements": [
        "business requirements",
        "requirements gathering",
        "gathering requirements"
    ],
    "Requirements Management": ["requirements management"],
    "Stakeholder Management": [
        "stakeholder management",
        "stakeholder engagement",
        "stakeholder relationships"
    ],
    "Process Analysis": [
        "process analysis",
        "business process analysis"
    ],
    "Process Mapping": [
        "process mapping",
        "business process mapping"
    ],
    "Change Management": ["change management"],
    "Quality Assurance": [
        "quality assurance",
        "quality control"
    ],
    "Gap Analysis": ["gap analysis"],
    "Use Case Analysis": ["use case analysis", "use cases"],

    # Finance and Accounting
    "Financial Analysis": [
        "financial analysis",
        "financial analytics"
    ],
    "Financial Modeling": [
        "financial modeling",
        "financial modelling",
        "financial models"
    ],
    "Financial Reporting": ["financial reporting"],
    "Financial Planning": [
        "financial planning",
        "financial planning and analysis",
        "fp&a"
    ],
    "Forecasting": [
        "forecasting",
        "financial forecasting"
    ],
    "Budgeting": ["budgeting", "budget preparation"],
    "Treasury Management": [
        "treasury management",
        "treasury operations"
    ],
    "Cash Flow Management": [
        "cash flow management",
        "cash flow forecasting",
        "cashflow management",
        "cashflow forecasting"
    ],
    "Risk Management": [
        "risk management",
        "financial risk management"
    ],
    "Investment Banking": ["investment banking"],
    "Corporate Finance": ["corporate finance"],
    "Revenue Management": ["revenue management"],

    # Supply Chain and Operations
    "Supply Chain Management": [
        "supply chain management",
        "supply chain"
    ],
    "Demand Planning": ["demand planning", "demand forecasting"],
    "Inventory Management": [
        "inventory management",
        "inventory control"
    ],
    "Procurement": ["procurement"],
    "Operations Management": ["operations management"],
    "Working Capital Management": ["working capital management"],

    # Compliance and Security
    "Compliance": [
        "compliance",
        "regulatory compliance",
        "material compliance"
    ],
    "Sustainability": ["sustainability"],
    "Cybersecurity": [
        "cybersecurity",
        "cyber security",
        "information security"
    ],
    "Information Security": ["information security"],
    "Data Privacy": ["data privacy", "data protection"],

    # Other Professional Skills
    "Training": [
        "training",
        "employee training",
        "technical training"
    ],
    "Market Research": ["market research"],
    "Strategic Planning": ["strategic planning"],
    "Client Relationship Management": [
        "client relationship management",
        "customer relationship management"
    ],
}


# --------------------------------------------------
# READ SILVER DATA
# --------------------------------------------------

def load_silver_jobs():
    input_file = SILVER_DATA / "silver_jobs.json"

    if not input_file.exists():
        raise FileNotFoundError(
            f"Silver file not found: {input_file}"
        )

    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Silver jobs data must be a JSON list.")

    return data


# --------------------------------------------------
# BUILD SKILL PATTERNS
# --------------------------------------------------

def build_skill_pattern(alias):
    """
    Build a case-insensitive regex pattern.
    Supports multiple spaces and punctuation in aliases.
    """

    alias = alias.strip()

    escaped_alias = re.escape(alias)
    escaped_alias = escaped_alias.replace(r"\ ", r"\s+")

    return re.compile(
        r"(?<![a-zA-Z0-9_])"
        + escaped_alias
        + r"(?![a-zA-Z0-9_])",
        re.IGNORECASE
    )


# --------------------------------------------------
# SKILL MATCHING
# --------------------------------------------------

def extract_skills(description):
    if not isinstance(description, str) or not description.strip():
        return []

    found_skills = set()

    for canonical_skill, aliases in SKILL_DICTIONARY.items():

        for alias in aliases:

            if not alias.strip():
                continue

            pattern = build_skill_pattern(alias)

            if pattern.search(description):
                found_skills.add(canonical_skill)
                break

    return sorted(found_skills)


# --------------------------------------------------
# INSPECT JOBS WITHOUT SKILLS
# --------------------------------------------------

def inspect_jobs_without_skills(limit=20):
    """
    Inspect jobs that have descriptions but no extracted skills.
    Does not modify or save output files.
    """

    jobs = load_silver_jobs()
    no_skill_jobs = []

    for job in jobs:

        description = job.get("description") or ""

        if not isinstance(description, str):
            continue

        if not description.strip():
            continue

        extracted_skills = extract_skills(description)

        if not extracted_skills:
            no_skill_jobs.append({
                "title": job.get("title"),
                "company": job.get("company"),
                "source": job.get("source"),
                "description": description[:500]
            })

    print("\nJOBS WITH DESCRIPTIONS BUT NO EXTRACTED SKILLS")
    print("=" * 55)
    print(f"Total: {len(no_skill_jobs)}")

    for index, job in enumerate(no_skill_jobs[:limit], 1):

        print(f"\n{index}. {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Source: {job['source']}")
        print(f"Description: {job['description']}")

    return no_skill_jobs


# --------------------------------------------------
# SKILL EXTRACTION PIPELINE
# --------------------------------------------------

def run_skill_extraction():

    jobs = load_silver_jobs()

    processed_jobs = []
    skill_counter = Counter()

    jobs_with_description = 0
    jobs_with_skills = 0

    for job in jobs:

        if not isinstance(job, dict):
            continue

        description = job.get("description")

        extracted_skills = extract_skills(description)

        job["extracted_skills"] = extracted_skills
        job["skill_extraction_method"] = "dictionary_matching"

        if job.get("has_description"):
            jobs_with_description += 1

        if extracted_skills:
            jobs_with_skills += 1

        skill_counter.update(extracted_skills)

        processed_jobs.append(job)

    # --------------------------------------------------
    # SAVE PROCESSED JOBS
    # --------------------------------------------------

    GOLD_DATA.mkdir(parents=True, exist_ok=True)

    output_file = GOLD_DATA / "jobs_with_skills.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            processed_jobs,
            file,
            ensure_ascii=False,
            indent=4,
            allow_nan=False
        )

    # --------------------------------------------------
    # BUILD SKILL SUMMARY
    # --------------------------------------------------

    skill_summary = {
        "total_jobs": len(processed_jobs),
        "jobs_with_descriptions": jobs_with_description,
        "jobs_with_extracted_skills": jobs_with_skills,
        "jobs_without_extracted_skills": (
            len(processed_jobs) - jobs_with_skills
        ),
        "unique_skills": len(skill_counter),
        "skills_frequency": dict(
            skill_counter.most_common()
        )
    }

    summary_file = GOLD_DATA / "skill_summary.json"

    with open(summary_file, "w", encoding="utf-8") as file:
        json.dump(
            skill_summary,
            file,
            ensure_ascii=False,
            indent=4,
            allow_nan=False
        )

    # --------------------------------------------------
    # PRINT RESULTS
    # --------------------------------------------------

    print("\nSkill Extraction completed!")

    print(f"Total jobs: {len(processed_jobs)}")
    print(f"Jobs with descriptions: {jobs_with_description}")
    print(f"Jobs with extracted skills: {jobs_with_skills}")

    print(
        f"Jobs without extracted skills: "
        f"{len(processed_jobs) - jobs_with_skills}"
    )

    print(f"Unique skills found: {len(skill_counter)}")

    print("\nTop 20 skills:")

    for skill, count in skill_counter.most_common(20):
        print(f"{skill}: {count}")

    print(f"\nJobs file saved to: {output_file}")
    print(f"Summary saved to: {summary_file}")

    return processed_jobs


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    # Run the full extraction pipeline
    run_skill_extraction()

    # To inspect jobs without skills instead:
    # Comment the line above and uncomment this:
    # inspect_jobs_without_skills(limit=20)
