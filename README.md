# Reddit Job Post Scraper & Analyzer

Automated pipeline for scraping job posts from Reddit and analyzing them with AI to extract structured data, plus a web interface to browse and search jobs.

## Features

- 🤖 **Automated Scraping**: Scheduled scraper runs every 2 hours via cron
- 💾 **PostgreSQL Storage**: Stores both raw and processed job post data
- 🔄 **Async Processing**: RabbitMQ queue for decoupled LLM processing
- 🧠 **AI Analysis**: Uses Llama 3.1 via Ollama (free, self-hosted) to extract:
  - Cleaned title and description
  - Job tags (type, level, technologies, location, etc.)
- 🌐 **Web Frontend**: Next.js app to browse, search, and filter jobs
- 📊 **REST API**: FastAPI backend with filtering and pagination
- 🐳 **Fully Dockerized**: One command to run everything
- ⚡ **GPU Support**: Optional GPU acceleration for 3-5x faster processing

## Architecture

```
Reddit Scraper (Cron)
    ↓
PostgreSQL Database ←→ FastAPI (REST API) ←→ Next.js Frontend
    ↓                      ↓
RabbitMQ Queue         Port 8000           Port 3000
    ↓
LLM Consumer (Ollama + Llama 3.1)
    ↓
Updated Database with Cleaned Data
```

## Quick Start

1. **Prerequisites:**
   - Docker & Docker Compose
   - Reddit API credentials ([get them here](https://www.reddit.com/prefs/apps))

2. **Configure:**
   ```bash
   # Reddit scraper config
   cp reddit_scraper/.env.template reddit_scraper/.env
   # Edit and add your Reddit API credentials

   # LLM service config (defaults are fine)
   cp llm_service/.env.template llm_service/.env
   ```

3. **Run:**
   ```bash
   docker compose build
   docker compose up -d
   ```

4. **Monitor:**
   ```bash
   docker compose logs -f
   ```

That's it! The system will:
- Scrape Reddit every 2 hours
- Store raw data in PostgreSQL
- Process with LLM (downloads model on first run, ~5 min)
- Update database with cleaned data

## Web Interface

After starting the services, access:
- **Frontend**: http://localhost:3000 - Browse and search jobs
- **API Docs**: http://localhost:8000/docs - Interactive API documentation
- **RabbitMQ UI**: http://localhost:15672 - Queue management (guest/guest)

## Documentation

- **[FRONTEND_SETUP.md](FRONTEND_SETUP.md)** - Frontend setup and development guide
- **[DOCKER_FRONTEND.md](DOCKER_FRONTEND.md)** - Frontend Docker configuration
- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Complete Docker setup guide, commands, troubleshooting
- **[GPU_SETUP.md](GPU_SETUP.md)** - Optional GPU acceleration setup for faster processing

## Project Structure

```
reddit-job-posts-web-scraping/
├── frontend/               # Next.js web interface
│   ├── app/               # Pages and routes
│   ├── components/        # React components
│   ├── lib/               # API client & types
│   ├── Dockerfile
│   └── .env.local
├── api/                   # FastAPI backend
│   ├── src/
│   │   ├── main.py       # API routes
│   │   ├── models.py     # Database models
│   │   └── schemas.py    # API schemas
│   ├── Dockerfile
│   └── .env
├── reddit_scraper/        # Scraper service
│   ├── src/
│   │   ├── scraper.py    # Main scraper logic
│   │   ├── db/           # Database models
│   │   └── messaging/    # RabbitMQ publisher
│   ├── Dockerfile
│   └── .env.template
├── llm_service/          # LLM analyzer service
│   ├── src/
│   │   ├── consumer.py   # RabbitMQ consumer
│   │   ├── analyzer.py   # Ollama LLM integration
│   │   └── database.py   # PostgreSQL client
│   ├── Dockerfile
│   └── .env.template
├── cron/                 # Cron schedule config
├── docker-compose.yml    # Main orchestration
└── docker-compose.gpu.yml # GPU acceleration (optional)
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | Next.js web interface |
| API | 8000 | FastAPI REST backend |
| PostgreSQL | 5432 | Stores job post data |
| RabbitMQ | 5672 | Message queue |
| RabbitMQ UI | 15672 | Management interface |
| Scraper | - | Cron job (every 2h) |
| LLM Consumer | - | Background processor |

## Database Schema

**Table:** `raw_job_posts`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `reddit_id` | VARCHAR | Unique Reddit post ID |
| `title` | TEXT | Original title |
| `body` | TEXT | Original post body |
| `author` | VARCHAR | Reddit username |
| `created_utc` | TIMESTAMP | Post creation time |
| `score` | INTEGER | Reddit score |
| `url` | TEXT | Post URL |
| `subreddit` | VARCHAR | Source subreddit |
| `scraped_at` | TIMESTAMP | When scraped |
| `cleaned_title` | TEXT | AI-processed title |
| `cleaned_text` | TEXT | AI-processed summary |
| `tags` | JSON | Extracted tags/categories |
| `processed_at` | TIMESTAMP | When processed by LLM |

## Usage Examples

**View unprocessed jobs:**
```bash
docker compose exec postgres psql -U reddit_user -d reddit_jobs -c \
  "SELECT id, title FROM raw_job_posts WHERE processed_at IS NULL;"
```

**View processed jobs with tags:**
```bash
docker compose exec postgres psql -U reddit_user -d reddit_jobs -c \
  "SELECT id, cleaned_title, tags FROM raw_job_posts WHERE processed_at IS NOT NULL LIMIT 5;"
```

**Check processing stats:**
```bash
docker compose exec postgres psql -U reddit_user -d reddit_jobs -c \
  "SELECT
    COUNT(*) FILTER (WHERE processed_at IS NULL) as unprocessed,
    COUNT(*) FILTER (WHERE processed_at IS NOT NULL) as processed
   FROM raw_job_posts;"
```

**RabbitMQ Management UI:**
- Open http://localhost:15672
- Login: `guest` / `guest`
- View queue status and consumer activity

## Performance

| Mode | Speed per Post | Recommended For |
|------|---------------|-----------------|
| CPU | 2-3 seconds | ~100-200 posts/day |
| GPU | 0.5-1 second | 500+ posts/day |

## Technologies

- **Python 3.11**
- **PostgreSQL 16** - Database
- **RabbitMQ 3.12** - Message queue
- **Ollama** - LLM inference engine
- **Llama 3.1 8B** - Language model
- **Docker** - Containerization
- **PRAW** - Reddit API wrapper
- **SQLAlchemy** - ORM
- **Pika** - RabbitMQ client

## License

MIT

## Requirements

- Docker & Docker Compose
- Reddit API credentials (free)
- 8GB+ RAM for LLM service
- (Optional) NVIDIA GPU for faster processing