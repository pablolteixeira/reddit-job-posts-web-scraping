import os
import praw
from dotenv import load_dotenv
from datetime import datetime
from db.models import RawJobPost, get_db_session, init_database
from messaging.publisher import RabbitMQPublisher

def load_reddit_client():
    """Initialize and return Reddit API client."""
    load_dotenv()
    
    return praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT')
    )

def scrape_job_posts(subreddits=['forhire'], limit=100):
    """
    ['forhire', 'jobbit', 'remotejs', 'remotepython']
    Scrape job posts from specified subreddits.
    
    Args:
        subreddits (list): List of subreddit names to scrape
        limit (int): Maximum number of posts to scrape per subreddit
    
    Returns:
        list: List of dictionaries containing post data
    """
    reddit = load_reddit_client()
    job_posts = []
    
    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        
        # Search for posts with [Hiring] tag
        for post in subreddit.search('[Hiring]', limit=limit):
            post_data = {
                'title': post.title,
                'body': post.selftext,
                'author': str(post.author),
                'created_utc': datetime.fromtimestamp(post.created_utc),
                'score': post.score,
                'url': post.url,
                'subreddit': subreddit_name,
                'id': post.id
            }
            job_posts.append(post_data)
    
    return job_posts

def save_to_database(job_posts):
    """
    Save scraped job posts to PostgreSQL database.

    Args:
        job_posts (list): List of dictionaries containing post data

    Returns:
        list: List of database row IDs for successfully inserted posts
    """
    session = get_db_session()
    inserted_ids = []

    try:
        for post_data in job_posts:
            # Check if post already exists
            existing_post = session.query(RawJobPost).filter_by(
                reddit_id=post_data['id']
            ).first()

            if existing_post:
                print(f"Post {post_data['id']} already exists, skipping...")
                continue

            # Create new job post record
            job_post = RawJobPost(
                reddit_id=post_data['id'],
                title=post_data['title'],
                body=post_data['body'],
                author=post_data['author'],
                created_utc=post_data['created_utc'],
                score=post_data['score'],
                url=post_data['url'],
                subreddit=post_data['subreddit']
            )

            session.add(job_post)
            session.flush()  # Get the ID without committing
            inserted_ids.append(job_post.id)
            print(f"Inserted post {post_data['id']} with DB ID {job_post.id}")

        session.commit()
        print(f"Successfully saved {len(inserted_ids)} new posts to database")

    except Exception as e:
        session.rollback()
        print(f"Error saving to database: {e}")
        raise
    finally:
        session.close()

    return inserted_ids


def publish_to_queue(job_ids):
    """
    Publish job post IDs to RabbitMQ for processing by LLM service.

    Args:
        job_ids (list): List of database row IDs
    """
    if not job_ids:
        print("No new job IDs to publish")
        return

    publisher = RabbitMQPublisher()
    try:
        publisher.connect()
        publisher.publish_job_ids(job_ids)
        print(f"Published {len(job_ids)} job IDs to queue")
    except Exception as e:
        print(f"Error publishing to queue: {e}")
        raise
    finally:
        publisher.close()


def main():
    # Load environment variables
    load_dotenv()

    # Initialize database tables
    print("Initializing database...")
    init_database()

    # Scrape job posts
    print("Scraping job posts...")
    job_posts = scrape_job_posts()
    print(f"Scraped {len(job_posts)} job posts")

    if not job_posts:
        print("No job posts found")
        return

    # Save to database
    print("Saving to database...")
    inserted_ids = save_to_database(job_posts)

    # Publish to RabbitMQ queue
    if inserted_ids:
        print("Publishing to message queue...")
        publish_to_queue(inserted_ids)
    else:
        print("No new posts to publish to queue")

if __name__ == "__main__":
    main()