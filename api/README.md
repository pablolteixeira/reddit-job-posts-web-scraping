# Reddit Job Posts API

A FastAPI-based REST API to query job posts scraped from Reddit with LLM-cleaned data.

## Features

- **No Authentication Required**: Public API for reading job post data
- **Advanced Filtering**: Filter by search terms, tags, date ranges, and more
- **Pagination**: Efficient pagination with customizable page sizes
- **Sorting**: Sort results by various fields (created_utc, processed_at, score)
- **Tag Search**: Query posts by specific tags (OR logic for multiple tags)
- **Statistics**: Get database statistics and all available tags
- **Auto-generated Documentation**: Interactive API docs via Swagger UI

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database (running via docker-compose from main project)

### Installation

1. **Install dependencies**:
   ```bash
   cd api
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   Copy `.env.example` to `.env` and update if needed:
   ```bash
   cp .env.example .env
   ```

3. **Ensure database is running**:
   From the project root:
   ```bash
   docker-compose up -d postgres
   ```

### Running the API

**Option 1: Using the run script**
```bash
./run.sh
```

**Option 2: Using uvicorn directly**
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Option 3: Using Docker**
```bash
docker build -t reddit-job-api .
docker run -p 8000:8000 --env-file .env reddit-job-api
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check

- **GET** `/health` - Check API and database connectivity

### Job Posts

#### Get Filtered Job Posts

**GET** `/api/v1/job-posts`

Query parameters:
- `page` (int, default: 1) - Page number
- `page_size` (int, default: 20, max: 100) - Items per page
- `search` (string) - Search in cleaned_title and cleaned_text
- `tags` (string) - Comma-separated tags (OR logic)
- `from_date` (datetime) - Filter from this date (ISO 8601)
- `to_date` (datetime) - Filter until this date (ISO 8601)
- `has_cleaned_data` (boolean) - Filter by cleaned data availability
- `sort_by` (string, default: "created_utc") - Sort field
- `sort_order` (string, default: "desc") - Sort order (asc/desc)

**Example requests:**

```bash
# Get first page of posts
curl "http://localhost:8000/api/v1/job-posts"

# Search for Python jobs
curl "http://localhost:8000/api/v1/job-posts?search=python"

# Filter by tags
curl "http://localhost:8000/api/v1/job-posts?tags=remote,python"

# Filter by date range
curl "http://localhost:8000/api/v1/job-posts?from_date=2024-01-01T00:00:00&to_date=2024-12-31T23:59:59"

# Only posts with cleaned data
curl "http://localhost:8000/api/v1/job-posts?has_cleaned_data=true"

# Combine multiple filters
curl "http://localhost:8000/api/v1/job-posts?search=developer&tags=remote&has_cleaned_data=true&page_size=50"
```

**Response example:**

```json
{
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8,
  "data": [
    {
      "id": 1,
      "cleaned_title": "Senior Python Developer - Remote",
      "cleaned_text": "We are looking for an experienced Python developer...",
      "tags": ["python", "remote", "senior", "backend"],
      "created_utc": "2024-11-12T10:30:00",
      "url": "https://reddit.com/r/forhire/..."
    }
  ]
}
```

#### Get Job Post by ID

**GET** `/api/v1/job-posts/{post_id}`

**Example:**

```bash
curl "http://localhost:8000/api/v1/job-posts/123"
```

### Tags

#### Get All Tags

**GET** `/api/v1/tags`

Returns a sorted list of all unique tags in the database.

**Example:**

```bash
curl "http://localhost:8000/api/v1/tags"
```

**Response:**

```json
["backend", "frontend", "python", "remote", "senior", "javascript"]
```

### Statistics

#### Get Database Stats

**GET** `/api/v1/stats`

**Example:**

```bash
curl "http://localhost:8000/api/v1/stats"
```

**Response:**

```json
{
  "total_posts": 1500,
  "posts_with_cleaned_data": 1200,
  "posts_without_cleaned_data": 300,
  "oldest_post_date": "2024-01-01T00:00:00",
  "newest_post_date": "2024-11-12T15:30:00"
}
```

## Data Model

The API returns the following fields for each job post:

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique post identifier |
| `cleaned_title` | string (nullable) | LLM-cleaned job title |
| `cleaned_text` | string (nullable) | LLM-cleaned job description |
| `tags` | array (nullable) | Array of tags extracted by LLM |
| `created_utc` | datetime | When the post was created on Reddit |
| `url` | string (nullable) | Reddit post URL |

## Configuration

Environment variables (in `.env` file):

```env
# PostgreSQL Database
POSTGRES_USER=reddit_user
POSTGRES_PASSWORD=reddit_password
POSTGRES_DB=reddit_jobs
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

## Integration with Docker Compose

To add the API to the existing docker-compose setup, add this service:

```yaml
api:
  build:
    context: ./api
    dockerfile: Dockerfile
  container_name: reddit-api
  env_file:
    - ./api/.env
  environment:
    POSTGRES_HOST: postgres
    POSTGRES_PORT: 5432
  ports:
    - "8000:8000"
  depends_on:
    postgres:
      condition: service_healthy
  restart: unless-stopped
```

## Development

### Project Structure

```
api/
├── src/
│   ├── __init__.py
│   ├── main.py          # FastAPI application and endpoints
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── database.py      # Database configuration
│   └── config.py        # Settings management
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── .env.example        # Example environment variables
├── .env                # Environment variables (gitignored)
├── run.sh             # Development run script
└── README.md          # This file
```

### Adding New Endpoints

1. Define Pydantic schemas in [src/schemas.py](src/schemas.py)
2. Add endpoint logic in [src/main.py](src/main.py)
3. Test using the interactive docs at `/docs`

## Testing

### Using the Interactive Docs

1. Start the API
2. Open http://localhost:8000/docs
3. Try out endpoints directly in the browser

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Get statistics
curl http://localhost:8000/api/v1/stats

# Search with filters
curl "http://localhost:8000/api/v1/job-posts?search=python&page_size=5"
```

### Using Python

```python
import requests

# Get job posts
response = requests.get(
    "http://localhost:8000/api/v1/job-posts",
    params={
        "search": "python",
        "tags": "remote,senior",
        "has_cleaned_data": True,
        "page": 1,
        "page_size": 20
    }
)

data = response.json()
print(f"Total posts: {data['total']}")
for post in data['data']:
    print(f"- {post['cleaned_title']}")
```

## Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable (database connection issues)

Error response format:

```json
{
  "detail": "Error message description"
}
```

## Performance Considerations

- **Pagination**: Always use pagination for large result sets
- **Indexing**: The database has indexes on `reddit_id` and `created_utc`
- **Connection Pooling**: Configured with pool_size=10, max_overflow=20
- **CORS**: Enabled for all origins (adjust in production if needed)

## License

This project is part of the reddit-job-posts-web-scraping system.
