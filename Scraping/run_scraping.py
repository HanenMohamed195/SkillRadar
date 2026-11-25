
from jobspy_source import fetch_jobs, save_jobs
from remotive_api import fetch_remotive_jobs, save_remotive_jobs


REMOTIVE_SEARCH_TERMS = [
    "data analyst",
    "data scientist",
    "data engineer",
    "python",
    "business analyst",
    "machine learning",
    "software engineer",
    "frontend",
    "backend",
    "SQL"
]


def collect_jobspy():
    print("\nStarting JobSpy collection...")

    try:
        jobs_df = fetch_jobs()
        save_jobs(jobs_df)

    except Exception as error:
        print(f"JobSpy failed: {error}")


def collect_remotive():
    print("\nStarting Remotive collection...")

    try:
        all_jobs = []

        for term in REMOTIVE_SEARCH_TERMS:
            print(f"\nSearching Remotive for: {term}")

            try:
                jobs = fetch_remotive_jobs(search=term)
                all_jobs.extend(jobs)

                print(f"Found {len(jobs)} jobs")

            except Exception as error:
                print(f"Remotive search failed for {term}: {error}")

        # إزالة التكرار حسب رابط الوظيفة
        unique_jobs = {}

        for job in all_jobs:
            key = job.get("job_url") or job.get("external_id")

            if key:
                unique_jobs[key] = job

        final_jobs = list(unique_jobs.values())

        save_remotive_jobs(final_jobs)

        print(f"\nTotal unique Remotive jobs: {len(final_jobs)}")

    except Exception as error:
        print(f"Remotive failed: {error}")


def main():
    print("Starting SkillRadar collection...")

    collect_jobspy()
    collect_remotive()

    print("\nCollection finished!")


if __name__ == "__main__":
    main()
