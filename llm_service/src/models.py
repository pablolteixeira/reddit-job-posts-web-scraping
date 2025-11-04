from pydantic import BaseModel
from typing import List, Optional

class JobPost(BaseModel):
    title: str
    body: str
    subreddit: str
    url: str
    created_utc: str
    
class JobAnalysis(BaseModel):
    skills_required: List[str]
    experience_level: str
    job_type: str
    salary_range: Optional[str]
    location: Optional[str]
    remote_policy: str
    company_info: Optional[str]
    key_responsibilities: List[str]