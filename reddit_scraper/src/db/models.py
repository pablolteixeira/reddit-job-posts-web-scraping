from sqlalchemy import Column, String, Integer, DateTime, Text, create_engine, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class RawJobPost(Base):
    """
    Table to store raw job post data from Reddit and cleaned data from LLM service.

    Raw columns are filled by the scraper.
    Cleaned columns (nullable) are filled by the LLM microservice.
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

    # Metadata
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Cleaned data (filled by LLM service, nullable initially)
    cleaned_title = Column(Text, nullable=True)
    cleaned_text = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)  # Store as JSON array
    processed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<RawJobPost(id={self.id}, reddit_id={self.reddit_id}, title={self.title[:50]})>"


def get_database_url():
    """Construct database URL from environment variables."""
    return (
        f"postgresql://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:"
        f"{os.getenv('POSTGRES_PORT')}/"
        f"{os.getenv('POSTGRES_DB')}"
    )


def get_db_engine():
    """Create and return database engine."""
    database_url = get_database_url()
    return create_engine(database_url)


def get_db_session():
    """Create and return database session."""
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_database():
    """Initialize database tables."""
    engine = get_db_engine()
    Base.metadata.create_all(engine)
    print("Database tables created successfully")
