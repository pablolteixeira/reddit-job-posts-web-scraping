# Reddit Job Posts Scraper

This project scrapes job posts from various job-related subreddits using the Reddit API.

## Setup

1. Create a Reddit account and register a new application at https://www.reddit.com/prefs/apps
2. Copy your client ID and client secret
3. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
4. Update the `.env` file with your Reddit API credentials:
```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=your_app_name_v1.0
```

## Usage

Run the scraper:
```bash
python src/scraper.py
```

The script will:
1. Scrape job posts from specified subreddits (default: r/forhire, r/jobbit, r/remotejs, r/remotepython)
2. Extract relevant information from each post
3. Save the data to a CSV file in the `data` directory with a timestamp

## Data Structure

The scraped data includes:
- Title
- Body
- Author
- Created date/time
- Score
- URL
- Subreddit
- Post ID

## Configuration

You can modify the following in `src/scraper.py`:
- Target subreddits
- Number of posts to scrape per subreddit
- Output file format and location