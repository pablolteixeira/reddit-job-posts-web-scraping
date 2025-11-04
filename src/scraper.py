import os
import praw
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

def load_reddit_client():
    """Initialize and return Reddit API client."""
    load_dotenv()
    
    return praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT')
    )

def scrape_job_posts(subreddits=['forhire', 'jobbit', 'remotejs', 'remotepython'], limit=100):
    """
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

def save_to_csv(job_posts, filename):
    """
    Save scraped job posts to a CSV file.
    
    Args:
        job_posts (list): List of dictionaries containing post data
        filename (str): Name of the output file
    """
    df = pd.DataFrame(job_posts)
    df.to_csv(filename, index=False)
    print(f"Saved {len(job_posts)} posts to {filename}")

def main():
    # Scrape job posts
    job_posts = scrape_job_posts()
    
    # Generate filename with current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/job_posts_{timestamp}.csv"
    
    # Save to CSV
    save_to_csv(job_posts, filename)

if __name__ == "__main__":
    main()