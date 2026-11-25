
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Make the project root accessible
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from matching.matcher import get_ranked_jobs

# Page configuration
st.set_page_config(
    page_title="SkillRadar",
    page_icon="🎯",
    layout="wide"
)

# Load available skills
SKILLS_FILE = ROOT_DIR / "data" / "skills.csv"

st.title("🎯 SkillRadar")
st.subheader("Find the right job based on your skills")
st.write(
    "Select your skills and discover remote jobs that match your profile."
)

st.divider()

# Skills selection
st.header("1. Select Your Skills")

try:
    skills_df = pd.read_csv(SKILLS_FILE)
    available_skills = sorted(
        skills_df["skill"].dropna().unique().tolist()
    )

    user_skills = st.multiselect(
        "What skills do you have?",
        options=available_skills,
        placeholder="Choose your skills..."
    )

except Exception as error:
    st.error(f"Could not load skills: {error}")
    st.stop()

# Search button
if st.button("Find Matching Jobs", type="primary"):

    if not user_skills:
        st.warning("Please select at least one skill.")
        st.session_state["user_skills"] = []

    else:
        st.session_state["user_skills"] = user_skills

# Display results
if st.session_state.get("user_skills"):

    selected_skills = st.session_state["user_skills"]

    st.divider()
    st.header("2. Your Matching Jobs")

    st.write("Your selected skills:", ", ".join(selected_skills))

    try:
        ranked_jobs = get_ranked_jobs(selected_skills)

        if not ranked_jobs:
            st.info("No jobs found in the database.")

        else:
            st.success(f"Found {len(ranked_jobs)} jobs!")

            # Search and Match Score filters
            col1, col2 = st.columns(2)

            with col1:
                search_text = st.text_input(
                    "Search by job title or company"
                )

            with col2:
                min_score = st.slider(
                    "Minimum Match Score",
                    min_value=0,
                    max_value=100,
                    value=0,
                    step=5
                )

            # Filter jobs
            filtered_jobs = [
                job for job in ranked_jobs
                if search_text.lower() in (
                    str(job.get("title", "")) + " " +
                    str(job.get("company", ""))
                ).lower()
                and job.get("score") is not None
                and job.get("score") >= min_score
            ]
            # Dashboard Summary
            st.divider()
            st.subheader("📊 Your Matching Summary")

            valid_scores = [
                job["score"]
                for job in filtered_jobs
                if job.get("score") is not None
            ]

            total_matching_jobs = len(filtered_jobs)

            if valid_scores:
                average_score = sum(valid_scores) / len(valid_scores)
                best_score = max(valid_scores)
            else:
                average_score = 0
                best_score = 0

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Total Matching Jobs",
                    total_matching_jobs
                )
            with col2:
                st.metric(
                    "Average Match Score",
                    f"{average_score:.1f}%"
                )

            with col3:
                st.metric(
                    "Best Match Score",
                    f"{best_score:.1f}%"
                )

            st.divider()
            # Display Best Match
            if filtered_jobs:
                best_job = filtered_jobs[0]

                st.subheader(" Best Match for You")

                with st.container(border=True):
                    st.markdown(
                        f"### {best_job.get('title', 'Unknown Title')}"
                    )

                    st.write(
                        f"**Company:** {best_job.get('company', 'Unknown')}"
                    )

                    st.metric(
                        "Match Score",
                        f"{best_job['score']:.1f}%"
                    )

                    st.write(
                        "**Matched Skills:**",
                        ", ".join(best_job.get("matched_skills", []))
                    )

                    st.write(
                        "**Missing Skills:**",
                        ", ".join(best_job.get("missing_skills", []))
                    )

                    if best_job.get("url"):
                        st.link_button(
                            "View Best Job",
                            best_job["url"]
                        )

                st.divider()

            # Display matching jobs
            for index, job in enumerate(filtered_jobs, start=1):


                score = job.get("score")
                matched = job.get("matched_skills", [])
                missing = job.get("missing_skills", [])

                with st.container(border=True):

                    col1, col2 = st.columns([4, 1])

                    with col1:
                        st.subheader(
                            f"{index}. {job.get('title', 'Unknown Title')}"
                        )

                        st.write(
                            f"**Company:** {job.get('company', 'Unknown')}"
                        )

                        st.write(
                            f"**Location:** {job.get('location_text', 'Not specified')}"
                        )

                    with col2:
                        if score is not None:
                            st.metric("Match Score", f"{score:.1f}%")
                        else:
                            st.metric("Match Score", "Not available")

                    st.write("**Matched Skills:**")

                    if matched:
                        st.success(", ".join(matched))
                    else:
                        st.write("No matching skills found.")

                    st.write("**Missing Skills:**")

                    if missing:
                        st.warning(", ".join(missing))
                    else:
                        st.success("No missing skills!")

                    job_url = job.get("url")

                    if job_url:
                        st.link_button("View Original Job", job_url)

            if not filtered_jobs:
                st.info("No jobs match your search or selected Match Score.")

    except Exception as error:
        st.error(f"Could not retrieve jobs: {error}")
