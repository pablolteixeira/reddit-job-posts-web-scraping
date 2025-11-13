from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from .database import Base


class RawJobPost(Base):
    """
    SQLAlchemy model for raw_job_posts table.
    Matches the schema in reddit_scraper/src/db/models.py
    """
    __tablename__ = 'raw_job_posts'

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Raw data from Reddit
    reddit_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    body = Column(Text)
    author = Column(String(100))
    created_utc = Column(DateTime, nullable=False)
    score = Column(Integer)
    url = Column(Text)
    subreddit = Column(String(100))

    # Metadata
    scraped_at = Column(DateTime, nullable=False)

    # Cleaned data (filled by LLM service)
    cleaned_title = Column(Text, nullable=True)
    cleaned_text = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    processed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<RawJobPost(id={self.id}, reddit_id={self.reddit_id})>"
