# API Quick Start Guide

## Starting the API

### Method 1: Docker Compose (Recommended)

From the project root directory:

```bash
# Start all services including the API
docker-compose up -d

# Or start only postgres and API
docker-compose up -d postgres api
```

The API will be available at http://localhost:8000

### Method 2: Local Development

```bash
cd api

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Make sure PostgreSQL is running (via docker-compose)
cd ..
docker-compose up -d postgres

# Run the API
cd api
./run.sh
```

## Quick API Examples

### 1. Check if API is running

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### 2. Get database statistics

```bash
curl http://localhost:8000/api/v1/stats
```

### 3. Get first 10 job posts

```bash
curl "http://localhost:8000/api/v1/job-posts?page_size=10"
```

### 4. Search for Python jobs

```bash
curl "http://localhost:8000/api/v1/job-posts?search=python"
```

### 5. Filter by tags (e.g., remote and python)

```bash
curl "http://localhost:8000/api/v1/job-posts?tags=remote,python"
```

### 6. Get only posts with cleaned data

```bash
curl "http://localhost:8000/api/v1/job-posts?has_cleaned_data=true"
```

### 7. Filter by date range

```bash
curl "http://localhost:8000/api/v1/job-posts?from_date=2024-11-01T00:00:00&to_date=2024-11-12T23:59:59"
```

### 8. Get all available tags

```bash
curl http://localhost:8000/api/v1/tags
```

### 9. Complex query with multiple filters

```bash
curl "http://localhost:8000/api/v1/job-posts?search=developer&tags=remote,senior&has_cleaned_data=true&sort_by=created_utc&sort_order=desc&page=1&page_size=25"
```

### 10. Get a specific job post by ID

```bash
curl http://localhost:8000/api/v1/job-posts/123
```

## Interactive Documentation

Open your browser and visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive documentation where you can test all endpoints directly in your browser!

## Testing with Python

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Get job posts with filters
response = requests.get(
    f"{BASE_URL}/api/v1/job-posts",
    params={
        "search": "python developer",
        "tags": "remote",
        "has_cleaned_data": True,
        "page": 1,
        "page_size": 20
    }
)

if response.status_code == 200:
    data = response.json()
    print(f"Total posts found: {data['total']}")
    print(f"Showing page {data['page']} of {data['total_pages']}")

    for post in data['data']:
        print(f"\n{post['cleaned_title']}")
        print(f"Tags: {', '.join(post['tags']) if post['tags'] else 'None'}")
        print(f"URL: {post['url']}")
        print(f"Posted: {post['created_utc']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

## Common Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `page` | int | Page number (default: 1) | `page=2` |
| `page_size` | int | Items per page (default: 20, max: 100) | `page_size=50` |
| `search` | string | Search in title and text | `search=python` |
| `tags` | string | Comma-separated tags (OR) | `tags=remote,python` |
| `from_date` | datetime | Filter from date | `from_date=2024-11-01T00:00:00` |
| `to_date` | datetime | Filter to date | `to_date=2024-11-12T23:59:59` |
| `has_cleaned_data` | boolean | Filter by cleaned data | `has_cleaned_data=true` |
| `sort_by` | string | Sort field | `sort_by=created_utc` |
| `sort_order` | string | Sort order (asc/desc) | `sort_order=desc` |

## Stopping the API

If using Docker:
```bash
docker-compose down
```

If running locally:
Press `Ctrl+C` in the terminal where the API is running.

## Troubleshooting

### API won't start

1. Check if port 8000 is already in use:
   ```bash
   lsof -i :8000
   ```

2. Check database connection in `.env` file

3. Ensure PostgreSQL is running:
   ```bash
   docker-compose ps postgres
   ```

### Database connection errors

1. Verify PostgreSQL is healthy:
   ```bash
   docker-compose ps
   ```

2. Check database credentials in [api/.env](api/.env)

3. For local development, use `POSTGRES_HOST=localhost`
4. For Docker, use `POSTGRES_HOST=postgres`

### No data returned

The database might be empty. Run the scraper first:
```bash
docker-compose up reddit-scraper-cron
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the interactive docs at http://localhost:8000/docs
- Check the main project README for information about the scraper and LLM service
