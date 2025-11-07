# Reddit Job Post Scraper & Analyzer - Docker Setup

This project uses Docker Compose to run an automated job post scraping and analysis pipeline with PostgreSQL, RabbitMQ, and Ollama LLM.

## Architecture

The system consists of 4 services:
1. **PostgreSQL**: Stores raw job post data and LLM-processed data
2. **RabbitMQ**: Message queue for asynchronous job processing
3. **Reddit Scraper**: Cron job that scrapes Reddit every 2 hours, saves to DB, publishes to queue
4. **LLM Consumer**: Processes queued jobs with Llama 3.1 model via Ollama, extracts structured data

## Prerequisites

- Docker
- Docker Compose
- Reddit API credentials
- (Optional) NVIDIA GPU for faster LLM processing

## Quick Start

1. **Configure Reddit scraper environment:**
   ```bash
   cp reddit_scraper/.env.template reddit_scraper/.env
   ```
   Edit `reddit_scraper/.env` and fill in your Reddit API credentials:
   - `REDDIT_CLIENT_ID`
   - `REDDIT_CLIENT_SECRET`
   - `REDDIT_USER_AGENT`

2. **Configure LLM service environment:**
   ```bash
   cp llm_service/.env.template llm_service/.env
   ```
   (Defaults are fine for most cases)

3. **Build and start all services:**
   ```bash
   docker compose build
   docker compose up -d
   ```

   **First-time startup note:** The LLM service will download the Llama 3.1 8B model (~4.7GB) on first run. This takes 3-5 minutes.

4. **Monitor the services:**
   ```bash
   # View all logs
   docker compose logs -f

   # View specific service
   docker compose logs -f llm-consumer
   docker compose logs -f reddit-scraper-cron
   ```

## Schedule Configuration

The scraper runs **every 2 hours** by default. To modify the schedule:

1. Edit `cron/crontab`
2. Restart the container: `docker-compose restart`

### Cron Schedule Examples:

- Every 2 hours (current): `0 */2 * * *`
- Every hour: `0 * * * *`
- Every 6 hours: `0 */6 * * *`
- Daily at 9 AM: `0 9 * * *`
- Every day at midnight: `0 0 * * *`

## Commands

**Start all services:**
```bash
docker compose up -d
```

**Stop all services:**
```bash
docker compose down
```

**View logs:**
```bash
# All services
docker compose logs -f

# Specific services
docker compose logs -f reddit-scraper-cron
docker compose logs -f llm-consumer
docker compose logs -f postgres
docker compose logs -f rabbitmq
```

**Rebuild after code changes:**
```bash
docker compose build
docker compose up -d
```

**Run scraper manually (one-time):**
```bash
docker compose exec reddit-scraper-cron python src/scraper.py
```

**Restart services:**
```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart llm-consumer
```

## Data Flow

```
┌─────────────────┐
│ Reddit Scraper  │ (Cron: every 2 hours)
│  (forhire sub)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │ Saves raw job post data
│ raw_job_posts   │ (title, body, author, etc.)
└────────┬────────┘
         │
         │ Publishes job_id
         ▼
┌─────────────────┐
│    RabbitMQ     │ job_posts_queue
│   Message Queue │
└────────┬────────┘
         │
         │ Consumes job_id
         ▼
┌─────────────────┐
│  LLM Consumer   │ Fetches job post from DB
│ (Ollama+Llama)  │ Analyzes with LLM
└────────┬────────┘ Extracts: cleaned_title,
         │          cleaned_text, tags
         ▼
┌─────────────────┐
│   PostgreSQL    │ Updates cleaned columns
│ raw_job_posts   │ (processed data)
└─────────────────┘
```

**Processing:**
1. **Scraper** scrapes Reddit every 2 hours
2. **Saves** raw data to PostgreSQL `raw_job_posts` table
3. **Publishes** job IDs to RabbitMQ `job_posts_queue`
4. **LLM Consumer** reads from queue, fetches job data, analyzes with Llama 3.1
5. **Updates** cleaned columns in database (cleaned_title, cleaned_text, tags)

### Database Schema

Table: `raw_job_posts`

**Raw columns** (filled by scraper):
- `id` - Primary key
- `reddit_id` - Unique Reddit post ID
- `title`, `body`, `author`, `created_utc`, `score`, `url`, `subreddit`
- `scraped_at` - Timestamp

**Cleaned columns** (filled by LLM service, nullable):
- `cleaned_title` - Processed title
- `cleaned_text` - Processed text
- `tags` - JSON array of tags
- `processed_at` - Timestamp

## Services Access

**PostgreSQL Database:**
```bash
# Connect to database
docker compose exec postgres psql -U reddit_user -d reddit_jobs

# View all raw job posts
docker compose exec postgres psql -U reddit_user -d reddit_jobs -c "SELECT id, title, scraped_at FROM raw_job_posts LIMIT 10;"

# View processed job posts
docker compose exec postgres psql -U reddit_user -d reddit_jobs -c "SELECT id, cleaned_title, tags, processed_at FROM raw_job_posts WHERE processed_at IS NOT NULL LIMIT 10;"

# Count posts by processing status
docker compose exec postgres psql -U reddit_user -d reddit_jobs -c "SELECT
  COUNT(*) FILTER (WHERE processed_at IS NULL) as unprocessed,
  COUNT(*) FILTER (WHERE processed_at IS NOT NULL) as processed,
  COUNT(*) as total
FROM raw_job_posts;"
```

**RabbitMQ Management UI:**
- URL: http://localhost:15672
- Username: `guest` (default)
- Password: `guest` (default)
- View queues, messages, and consumer status

**Service Ports:**
- PostgreSQL: `localhost:5432`
- RabbitMQ AMQP: `localhost:5672`
- RabbitMQ Management: `localhost:15672`

## GPU Acceleration (Optional)

The LLM service automatically detects and uses GPU if available. For faster processing:

1. See [GPU_SETUP.md](GPU_SETUP.md) for detailed instructions
2. Short version: Install `nvidia-container-toolkit` and reboot
3. Run with: `docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d`

**Performance:**
- CPU mode: ~2-3 seconds per job post
- GPU mode: ~0.5-1 second per job post

## Troubleshooting

**Check service status:**
```bash
docker compose ps
```

**Service won't start:**
```bash
# Check logs for errors
docker compose logs llm-consumer
docker compose logs reddit-scraper-cron

# Rebuild if code changed
docker compose build
docker compose up -d
```

**LLM consumer stuck on "Pulling model":**
- First run downloads 4.7GB model (takes 3-5 minutes)
- Check progress: `docker compose logs -f llm-consumer`

**No jobs being processed:**
```bash
# Check if RabbitMQ has messages
docker compose exec rabbitmq rabbitmqctl list_queues

# Check if consumer is connected
docker compose logs llm-consumer | grep "Connected to RabbitMQ"

# Manually run scraper to add jobs
docker compose exec reddit-scraper-cron python src/scraper.py
```

**Database connection issues:**
```bash
# Check if postgres is healthy
docker compose ps postgres

# Test connection
docker compose exec postgres pg_isready -U reddit_user -d reddit_jobs
```

**Clean up and restart fresh:**
```bash
# Stop and remove containers + volumes (deletes all data!)
docker compose down -v

# Rebuild and start
docker compose build
docker compose up -d
```

## Performance Tuning

**Adjust LLM model size** (in `llm_service/.env`):
```bash
# Smaller, faster, less accurate
OLLAMA_MODEL=llama3.1:3b

# Default - good balance
OLLAMA_MODEL=llama3.1:8b

# Larger, slower, more accurate (requires more RAM)
OLLAMA_MODEL=llama3.1:70b
```

**Adjust scraper schedule** (in `cron/crontab`):
- More frequent = more data, higher load
- Less frequent = less data, lower load

**Scale LLM consumers** (for high throughput):
```bash
# Run multiple consumers in parallel
docker compose up -d --scale llm-consumer=3
```
