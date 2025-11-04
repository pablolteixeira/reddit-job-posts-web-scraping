# Project Structure

This project consists of two main components:

1. Reddit Scraper (`reddit_scraper/`)
   - Scrapes job posts from various subreddits
   - Saves data in CSV format
   
2. LLM Service (`llm_service/`)
   - Analyzes job posts using GPT
   - Provides REST API for job post analysis
   - Extracts structured information from posts

## Setup

Each component has its own setup instructions in their respective directories:
- [Reddit Scraper Setup](reddit_scraper/README.md)
- [LLM Service Setup](llm_service/README.md)

## Workflow

1. Use the Reddit scraper to collect job posts
2. Process the collected data through the LLM service
3. Get structured analysis of job requirements, skills, and other details

## Requirements

- Python 3.8+
- Reddit API credentials
- OpenAI API key