from fastapi import FastAPI, HTTPException
from supabase_client import get_jobs

app = FastAPI(
    title="SkillRadar API",
    description="Smart Job Matching Platform",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Welcome to SkillRadar API",
        "status": "running"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "project": "SkillRadar"
    }


@app.get("/api/jobs")
def read_jobs():
    try:
        jobs = get_jobs()
        return {
            "total": len(jobs),
            "jobs": jobs
        }
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )