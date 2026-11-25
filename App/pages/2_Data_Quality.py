
import streamlit as st
import pandas as pd

from analytics.queries import (
    get_data_quality_summary,
    get_jobs_skills_summary,
    get_pipeline_history
)


# Page Title
st.title("🔍 Data Quality")
st.write(
    "Monitor data completeness, skill extraction, "
    "and pipeline execution history."
)

st.divider()


# 1. Get Data
quality = get_data_quality_summary()
skills = get_jobs_skills_summary()
pipeline = get_pipeline_history(limit=10)


# 2. Overview Metrics
st.subheader("Data Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Jobs", quality["total_jobs"])
col2.metric("Jobs With Skills", skills["jobs_with_skills"])
col3.metric("Jobs Without Skills", skills["jobs_without_skills"])

st.divider()


# 3. Missing Data Analysis
st.subheader("Missing Data Analysis")

missing_data = {
    "Field": [
        "Title",
        "Company",
        "Category",
        "URL"
    ],
    "Missing Records": [
        quality["missing_titles"] or 0,
        quality["missing_companies"] or 0,
        quality["missing_categories"] or 0,
        quality["missing_urls"] or 0
    ]
}

missing_df = pd.DataFrame(missing_data)

st.dataframe(
    missing_df,
    use_container_width=True,
    hide_index=True
)

total_missing = sum(missing_data["Missing Records"])

if total_missing == 0:
    st.success("No missing values found in the checked fields.")
else:
    st.warning(
        f"Found {total_missing} missing values "
        "in the checked fields."
    )

st.divider()


# 4. Skills Extraction Quality
st.subheader("Skills Extraction Analysis")

total_jobs = skills["total_jobs"] or 0
with_skills = skills["jobs_with_skills"] or 0
without_skills = skills["jobs_without_skills"] or 0

if total_jobs > 0:
    coverage = with_skills / total_jobs

    col1, col2 = st.columns(2)

    col1.metric(
        "Skills Coverage",
        f"{coverage:.1%}"
    )

    col2.metric(
        "Jobs Without Skills",
        without_skills
    )

    st.progress(coverage)

    skills_chart = pd.DataFrame({
        "Status": ["With Skills", "Without Skills"],
        "Jobs": [with_skills, without_skills]
    })

    st.bar_chart(
        skills_chart.set_index("Status")
    )
else:
    st.info("No jobs available for skills analysis.")

st.divider()


# 5. Pipeline Execution History
st.subheader("Pipeline Execution History")

if pipeline:

    pipeline_df = pd.DataFrame(pipeline)

    st.dataframe(
        pipeline_df,
        use_container_width=True,
        hide_index=True
    )

    successful_runs = sum(
        1 for run in pipeline
        if run["status"] == "success"
    )

    st.caption(
        f"{successful_runs} successful runs "
        f"out of {len(pipeline)} displayed runs."
    )

    failed_runs = [
        run for run in pipeline
        if run["status"] != "success"
    ]

    if failed_runs:
        st.warning("Some pipeline runs were not successful.")

        for run in failed_runs:
            st.write(
                f"Run #{run['run_id']}: "
                f"{run['error_message'] or run['status']}"
            )
    else:
        st.success("All displayed pipeline runs completed successfully.")

else:
    st.info("No pipeline execution history available yet.")

# 6. Data Source and Last Refresh
st.divider()
st.subheader("About the Data")

col1, col2 = st.columns(2)

col1.metric("Data Source", "Remotive API")

if pipeline:
    latest_run = pipeline[0]
    last_refresh = latest_run["started_at"]

    col2.metric("Last Refresh", "Available")
    st.caption(f"Last refresh time (UTC): {last_refresh}")

    st.subheader("Latest Pipeline Run")

    run_col1, run_col2, run_col3 = st.columns(3)

    run_col1.metric(
        "Retrieved",
        latest_run["retrieved"] or 0
    )

    run_col2.metric(
        "Inserted",
        latest_run["inserted"] or 0
    )

    run_col3.metric(
        "Updated",
        latest_run["updated"] or 0
    )

    run_col4, run_col5 = st.columns(2)

    run_col4.metric(
        "Skipped Invalid",
        latest_run["skipped_invalid"] or 0
    )

    run_col5.metric(
        "Jobs Without Skills",
        latest_run["no_skills_found"] or 0
    )

else:
    col2.metric("Last Refresh", "Not available")
    st.info("Run the pipeline to get refresh information.")


# 7. How Matching Works
st.divider()
st.subheader("How the Matching Score Works")

with st.expander("Understand the matching calculation"):
    st.write(
        "The matching score measures the percentage of job-required "
        "skills that the user already has."
    )

    st.latex(
        r"Score = \\frac{Matched\\ Skills}{Total\\ Job\\ Skills} \\times 100"
    )

    st.write("Example:")
    st.write(
        "A job requires Python, SQL, Excel, and Power BI. "
        "If the user has Python and SQL, the score is 50%."
    )

    st.write(
        "Missing skills are the required skills that the user "
        "has not selected."
    )

    st.info(
        "Jobs without detected skills have an unavailable score."
    )


# 8. Project Limitations
st.divider()
st.subheader("Project Limitations")

st.markdown("""
- Jobs are collected from the Remotive API and focus on remote opportunities.
- Job listings may expire or be closed after collection.
- Skill extraction depends on API tags and the skills dictionary.
- Some relevant skills may not be detected automatically.
- The matching score measures skill overlap only; it does not predict
  hiring probability or guarantee job acceptance.
- Data is refreshed manually by running the pipeline.
""")
