import streamlit as st
import pandas as pd

from analytics.queries import (
    get_total_jobs,
    get_jobs_by_category,
    get_top_skills,
    get_jobs_by_type,
    get_recent_jobs
)


# Page title
st.title("📊 Market Insights")
st.write(
    "Explore job market trends, popular skills, "
    "and the latest remote job opportunities."
)

st.divider()


# 1. Overview Metrics
total_jobs = get_total_jobs()

categories = get_jobs_by_category()
top_skills = get_top_skills(limit=10)
job_types = get_jobs_by_type()
recent_jobs = get_recent_jobs(limit=10)

total_categories = len(categories)
total_skills = sum(
    len(item) for item in top_skills
)

col1, col2, col3 = st.columns(3)

col1.metric("Total Jobs", total_jobs)
col2.metric("Job Categories", total_categories)
col3.metric("Top Skills Tracked", len(top_skills))

st.divider()


# 2. Jobs by Category
st.subheader("Jobs by Category")

if categories:
    category_df = pd.DataFrame(categories)

    st.bar_chart(
        category_df.set_index("category")["job_count"],
        horizontal=True
    )
else:
    st.info("No category data available.")


st.divider()


# 3. Most Requested Skills
st.subheader("Top Requested Skills")

if top_skills:
    skills_df = pd.DataFrame(top_skills)

    st.bar_chart(
        skills_df.set_index("skill")["job_count"],
        horizontal=True
    )
else:
    st.info("No skills data available.")


st.divider()


# 4. Jobs by Type
st.subheader("Jobs by Type")

if job_types:
    job_type_df = pd.DataFrame(job_types)

    st.bar_chart(
        job_type_df.set_index("job_type")["job_count"]
    )
else:
    st.info("No job type data available.")


st.divider()


# 5. Recent Jobs
st.subheader("Latest Job Opportunities")

if recent_jobs:

    for job in recent_jobs:

        with st.container(border=True):

            st.markdown(f"{job['title']}")

            company = job["company"] or "Not specified"
            category = job["category"] or "Not specified"
            published = job["published_at"] or "Not specified"

            st.caption(
                f"{company} | {category} | {published}"
            )

            st.link_button(
                "View Job",
                job["url"]
            )

else:
    st.info("No jobs available yet.")