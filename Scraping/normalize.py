
def normalize_job(job, source):
    return {
        "external_id": str(job.get("external_id") or ""),
        "title": job.get("title"),
        "company": job.get("company"),
        "description": job.get("description"),
        "location": job.get("location"),
        "salary": job.get("salary"),
        "job_type": job.get("job_type"),
        "category": job.get("category"),
        "skills": job.get("skills") or [],
        "posted_date": job.get("posted_date"),
        "job_url": job.get("job_url"),
        "source": source
    }
