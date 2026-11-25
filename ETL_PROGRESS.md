# SkillRadar – ETL Progress Report

## Completed Tasks

The ETL and Skill Processing stages have been completed.

- Collected 992 job records from Bayt, Indeed, and Remotive.
- Implemented the Medallion Architecture:
  - Bronze Layer
  - Silver Layer
  - Gold Layer
- Cleaned and prepared job data.
- Recovered missing job descriptions where possible.
- Implemented Skill Extraction.
- Implemented Skill Normalization using the Skill Taxonomy.
- Generated the following outputs:
  - `normalized_jobs.json`
  - `job_skill_dataset.json`
  - `skill_taxonomy.json`
  - `normalized_skill_summary.json`
- Executed Data Quality Checks.

## Data Quality Results

| Metric | Result |
|---|---:|
| Total Jobs | 992 |
| Jobs with Skills | 974 |
| Jobs without Skills | 18 |
| Job-Skill Rows | 7,040 |
| Unique Normalized Skills | 115 |
| Taxonomy Skills | 120 |
| PASS Checks | 16 |
| FAIL Checks | 0 |
| WARNING Checks | 2 |

Overall Status: **PASS_WITH_WARNINGS**

The two warnings are:
- One job has no available description.
- Eighteen jobs have no extracted skills.

These records were retained without inventing missing information.

## Remaining Tasks

1. Matching Engine – Calculate job-to-user skill compatibility and rank matching jobs.
2. Backend/API Integration – Connect the ETL outputs and Matching Engine to the backend.
3. Frontend – Display jobs and matching results.
4. Telegram Bot – Connect the bot to the API.
5. Power BI – Build dashboards for job and skill analysis.
6. Testing & Integration – Test the complete workflow.
7. Documentation – Complete project documentation.

## Current Status

The ETL, Skill Extraction, Skill Normalization, and Data Quality stages are complete. The next major step is implementing the Matching Engine and integrating the remaining project components.