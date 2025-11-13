from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class JobPostResponse(BaseModel):
    """Response schema for job post data."""
    id: int
    cleaned_title: Optional[str] = None
    cleaned_text: Optional[str] = None
    tags: Optional[List[str]] = None
    created_utc: datetime
    url: Optional[str] = None

    class Config:
        from_attributes = True


class JobPostListResponse(BaseModel):
    """Response schema for paginated job posts."""
    total: int
    page: int
    page_size: int
    total_pages: int
    data: List[JobPostResponse]


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
