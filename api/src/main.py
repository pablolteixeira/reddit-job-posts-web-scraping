from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from typing import Optional, List
from datetime import datetime
import math

from .database import get_db
from .models import RawJobPost
from .schemas import JobPostResponse, JobPostListResponse, ErrorResponse
from .config import get_settings

settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title="Reddit Job Posts API",
    description="API to query job posts scraped from Reddit with LLM-cleaned data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins since no authentication required
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check."""
    return {
        "message": "Reddit Job Posts API",
        "status": "healthy",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint that verifies database connectivity."""
    try:
        # Try to execute a simple query
        db.execute(func.now())
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")


@app.get(
    "/api/v1/job-posts",
    response_model=JobPostListResponse,
    tags=["Job Posts"],
    summary="Get filtered job posts",
    responses={
        200: {"description": "Successful response with filtered job posts"},
        400: {"model": ErrorResponse, "description": "Invalid query parameters"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def get_job_posts(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page (max 100)"),
    search: Optional[str] = Query(None, description="Search in cleaned_title and cleaned_text"),
    tags: Optional[str] = Query(None, description="Comma-separated list of tags to filter by (OR logic)"),
    from_date: Optional[datetime] = Query(None, description="Filter posts from this date (ISO 8601 format)"),
    to_date: Optional[datetime] = Query(None, description="Filter posts until this date (ISO 8601 format)"),
    has_cleaned_data: Optional[bool] = Query(None, description="Filter posts with/without cleaned data"),
    sort_by: str = Query("created_utc", description="Sort by field: created_utc, processed_at, score"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    db: Session = Depends(get_db)
):
    """
    Get job posts with filtering, searching, and pagination.

    **Filtering options:**
    - `search`: Text search in cleaned_title and cleaned_text
    - `tags`: Filter by specific tags (comma-separated, OR logic)
    - `from_date` & `to_date`: Filter by creation date range
    - `has_cleaned_data`: Only return posts with cleaned data (true) or without (false)

    **Sorting:**
    - `sort_by`: Field to sort by (created_utc, processed_at, score)
    - `sort_order`: asc (ascending) or desc (descending)

    **Pagination:**
    - `page`: Current page number (starts at 1)
    - `page_size`: Items per page (1-100)
    """
    try:
        # Build base query
        query = db.query(RawJobPost)

        # Apply filters
        filters = []

        # Filter by cleaned data availability
        if has_cleaned_data is True:
            filters.append(RawJobPost.cleaned_title.isnot(None))
        elif has_cleaned_data is False:
            filters.append(RawJobPost.cleaned_title.is_(None))

        # Search filter
        if search:
            search_term = f"%{search}%"
            search_filters = [
                RawJobPost.cleaned_title.ilike(search_term),
                RawJobPost.cleaned_text.ilike(search_term)
            ]
            filters.append(or_(*search_filters))

        # Tags filter (OR logic - match any of the provided tags)
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
            if tag_list:
                # Check if any of the tags in the list are in the JSON array
                # Using cast to text and LIKE for PostgreSQL JSON type
                from sqlalchemy import Text, cast
                tag_filters = []
                for tag in tag_list:
                    # Cast tags to text and check if it contains the tag
                    tag_filters.append(
                        cast(RawJobPost.tags, Text).like(f'%"{tag}"%')
                    )
                filters.append(or_(*tag_filters))

        # Date range filters
        if from_date:
            filters.append(RawJobPost.created_utc >= from_date)
        if to_date:
            filters.append(RawJobPost.created_utc <= to_date)

        # Apply all filters
        if filters:
            query = query.filter(and_(*filters))

        # Get total count before pagination
        total = query.count()

        # Apply sorting
        sort_order = sort_order.lower()
        if sort_order not in ["asc", "desc"]:
            raise HTTPException(status_code=400, detail="sort_order must be 'asc' or 'desc'")

        sort_field = getattr(RawJobPost, sort_by, None)
        if sort_field is None:
            raise HTTPException(status_code=400, detail=f"Invalid sort_by field: {sort_by}")

        if sort_order == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        # Execute query
        job_posts = query.all()

        # Calculate total pages
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        # Build response
        return JobPostListResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            data=[JobPostResponse.model_validate(post) for post in job_posts]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying job posts: {str(e)}")


@app.get(
    "/api/v1/job-posts/{post_id}",
    response_model=JobPostResponse,
    tags=["Job Posts"],
    summary="Get job post by ID",
    responses={
        200: {"description": "Job post found"},
        404: {"model": ErrorResponse, "description": "Job post not found"},
    }
)
async def get_job_post(post_id: int, db: Session = Depends(get_db)):
    """Get a specific job post by its ID."""
    job_post = db.query(RawJobPost).filter(RawJobPost.id == post_id).first()

    if not job_post:
        raise HTTPException(status_code=404, detail=f"Job post with id {post_id} not found")

    return JobPostResponse.model_validate(job_post)


@app.get(
    "/api/v1/tags",
    response_model=List[str],
    tags=["Tags"],
    summary="Get all unique tags",
    description="Returns a list of all unique tags found in job posts"
)
async def get_all_tags(db: Session = Depends(get_db)):
    """Get all unique tags from job posts."""
    try:
        # Query all non-null tags
        results = db.query(RawJobPost.tags).filter(RawJobPost.tags.isnot(None)).all()

        # Extract unique tags
        unique_tags = set()
        for (tags,) in results:
            if tags and isinstance(tags, list):
                unique_tags.update(tags)

        return sorted(list(unique_tags))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tags: {str(e)}")


@app.get(
    "/api/v1/stats",
    tags=["Statistics"],
    summary="Get database statistics",
    description="Returns overall statistics about the job posts database"
)
async def get_stats(db: Session = Depends(get_db)):
    """Get statistics about job posts in the database."""
    try:
        total_posts = db.query(func.count(RawJobPost.id)).scalar()
        posts_with_cleaned_data = db.query(func.count(RawJobPost.id)).filter(
            RawJobPost.cleaned_title.isnot(None)
        ).scalar()
        posts_without_cleaned_data = total_posts - posts_with_cleaned_data

        # Get date range
        oldest_post = db.query(func.min(RawJobPost.created_utc)).scalar()
        newest_post = db.query(func.max(RawJobPost.created_utc)).scalar()

        return {
            "total_posts": total_posts,
            "posts_with_cleaned_data": posts_with_cleaned_data,
            "posts_without_cleaned_data": posts_without_cleaned_data,
            "oldest_post_date": oldest_post,
            "newest_post_date": newest_post,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
