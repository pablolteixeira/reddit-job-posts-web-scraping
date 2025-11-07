"""
Database client for fetching and updating job posts in PostgreSQL.
"""
import os
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, create_engine, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


class RawJobPost(Base):
    """
    SQLAlchemy model matching the raw_job_posts table.
    """
    __tablename__ = 'raw_job_posts'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Raw data from Reddit (filled by scraper)
    reddit_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    body = Column(Text)
    author = Column(String(100))
    created_utc = Column(DateTime, nullable=False)
    score = Column(Integer)
    url = Column(Text)
    subreddit = Column(String(100))
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Cleaned data (filled by LLM service, nullable initially)
    cleaned_title = Column(Text, nullable=True)
    cleaned_text = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    processed_at = Column(DateTime, nullable=True)


class DatabaseClient:
    """Client for interacting with PostgreSQL database."""

    def __init__(self):
        self.database_url = self._get_database_url()
        self.engine = create_engine(self.database_url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def _get_database_url(self) -> str:
        """Construct database URL from environment variables."""
        return (
            f"postgresql://{os.getenv('POSTGRES_USER')}:"
            f"{os.getenv('POSTGRES_PASSWORD')}@"
            f"{os.getenv('POSTGRES_HOST')}:"
            f"{os.getenv('POSTGRES_PORT')}/"
            f"{os.getenv('POSTGRES_DB')}"
        )

    def fetch_job_post(self, job_id: int) -> Optional[RawJobPost]:
        """
        Fetch a job post by its ID.

        Args:
            job_id: Database ID of the job post

        Returns:
            RawJobPost object or None if not found
        """
        try:
            return self.session.query(RawJobPost).filter_by(id=job_id).first()
        except Exception as e:
            print(f"Error fetching job post {job_id}: {e}")
            return None

    def update_cleaned_data(
        self,
        job_id: int,
        cleaned_title: str,
        cleaned_text: str,
        tags: list
    ) -> bool:
        """
        Update cleaned data columns for a job post.

        Args:
            job_id: Database ID of the job post
            cleaned_title: Processed title
            cleaned_text: Processed text
            tags: List of tags/categories

        Returns:
            True if update successful, False otherwise
        """
        try:
            job_post = self.session.query(RawJobPost).filter_by(id=job_id).first()
            if not job_post:
                print(f"Job post {job_id} not found")
                return False

            job_post.cleaned_title = cleaned_title
            job_post.cleaned_text = cleaned_text
            job_post.tags = tags
            job_post.processed_at = datetime.utcnow()

            self.session.commit()
            print(f"Updated cleaned data for job post {job_id}")
            return True

        except Exception as e:
            self.session.rollback()
            print(f"Error updating job post {job_id}: {e}")
            return False

    def close(self):
        """Close database connection."""
        self.session.close()
