
from pipeline.extract import fetch_jobs, save_sample
from pipeline.transform import transform_jobs
from pipeline.load import load_jobs


def main():

    print("=" * 40)
    print("Starting SkillRadar Pipeline")
    print("=" * 40)

    # Step 1: Extract
    print("\nStep 1: Extracting jobs...")

    jobs = fetch_jobs()

    print(f"Retrieved {len(jobs)} jobs")

    # Save raw data
    save_sample(jobs)

    # Step 2: Transform
    print("\nStep 2: Transforming jobs...")

    cleaned_jobs = transform_jobs()

    print(f"Cleaned {len(cleaned_jobs)} jobs")

    # Step 3: Load
    print("\nStep 3: Loading into database...")

    load_jobs(cleaned_jobs)

    print("\n" + "=" * 40)
    print("SkillRadar Pipeline completed!")
    print("=" * 40)


if __name__ == "__main__":
    try:
        main()

    except Exception as error:
        print("\nPipeline failed!")
        print("Error:", error)
