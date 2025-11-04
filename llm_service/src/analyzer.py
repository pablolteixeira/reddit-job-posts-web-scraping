import os
from openai import OpenAI
from dotenv import load_dotenv
from .models import JobPost, JobAnalysis

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_job_post(job_post: JobPost) -> JobAnalysis:
    """
    Analyze a job post using OpenAI's GPT model to extract structured information.
    
    Args:
        job_post (JobPost): Job post data to analyze
        
    Returns:
        JobAnalysis: Structured analysis of the job post
    """
    prompt = f"""Analyze this job post and extract key information:
Title: {job_post.title}
Content: {job_post.body}

Please extract and structure the following information:
- Required skills and technologies
- Experience level required
- Job type (full-time, part-time, contract)
- Salary range (if mentioned)
- Location or remote work policy
- Company information
- Key responsibilities

Provide the analysis in a structured format."""

    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME", "gpt-4-1106-preview"),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=int(os.getenv("MAX_TOKENS", "1000")),
        temperature=0.5
    )
    
    # Process the response and structure it
    content = response.choices[0].message.content
    
    # TODO: Implement parsing logic for the GPT response
    # This is a placeholder implementation
    analysis = JobAnalysis(
        skills_required=["placeholder"],
        experience_level="Not specified",
        job_type="Not specified",
        salary_range=None,
        location=None,
        remote_policy="Not specified",
        company_info=None,
        key_responsibilities=["placeholder"]
    )
    
    return analysis