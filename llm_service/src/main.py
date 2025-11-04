from fastapi import FastAPI, HTTPException
from .models import JobPost, JobAnalysis
from .analyzer import analyze_job_post

app = FastAPI(
    title="Job Post Analyzer",
    description="API for analyzing Reddit job posts using LLM",
    version="1.0.0"
)

@app.post("/analyze", response_model=JobAnalysis)
async def analyze_post(job_post: JobPost):
    """
    Analyze a job post and extract structured information.
    """
    try:
        analysis = analyze_job_post(job_post)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}