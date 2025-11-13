# Quick Start Guide

Get the entire Reddit Job Posts system running in minutes!

## What You'll Get

- ✅ Web interface to browse and search jobs at http://localhost:3000
- ✅ REST API with documentation at http://localhost:8000/docs
- ✅ Automated scraping from Reddit every 2 hours
- ✅ AI-powered job post analysis and tagging
- ✅ Full-text search and tag filtering

## Prerequisites

1. **Docker & Docker Compose** installed
2. **Reddit API credentials** (free, takes 2 minutes)
   - Go to https://www.reddit.com/prefs/apps
   - Click "create app"
   - Choose "script"
   - Note your client_id and client_secret

## Step-by-Step Setup

### 1. Clone and Navigate

```bash
cd /path/to/reddit-job-posts-web-scraping
```

### 2. Configure Environment Files

**Reddit Scraper:**
```bash
cp reddit_scraper/.env.template reddit_scraper/.env
nano reddit_scraper/.env  # or use your preferred editor
```

Add your Reddit credentials:
```env
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=job_scraper_bot/1.0
```

**LLM Service (optional, defaults are fine):**
```bash
cp llm_service/.env.template llm_service/.env
```

**API (optional, defaults are fine):**
```bash
# API .env already exists, no changes needed
```

**Frontend (optional, defaults are fine):**
```bash
# Frontend .env.local already exists with default API URL
```

### 3. Build and Start

```bash
# Build all services
docker-compose build

# Start everything
docker-compose up -d
```

**First run notes:**
- Ollama will download Llama 3.1 model (~5 minutes, 4.7GB)
- This happens automatically in the background
- Check progress: `docker-compose logs -f llm-consumer`

### 4. Access the Application

**Wait ~30 seconds for services to start**, then:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Web Interface** | http://localhost:3000 | None needed |
| **API Docs** | http://localhost:8000/docs | None needed |
| **RabbitMQ UI** | http://localhost:15672 | guest / guest |

## What Happens Next?

### Immediate (0-5 minutes)
1. ✅ PostgreSQL database starts
2. ✅ RabbitMQ message queue starts
3. ✅ API backend starts
4. ✅ Frontend starts
5. ⏳ LLM service downloads model (~5 min first time only)

### Within 2 Hours
1. ✅ Reddit scraper runs for the first time
2. ✅ Job posts are scraped and saved to database
3. ✅ Posts are queued for AI processing
4. ✅ LLM analyzes posts and extracts structured data
5. ✅ Cleaned data appears in the web interface

### Ongoing
- 🔄 Scraper runs every 2 hours
- 🔄 New posts are automatically processed
- 🔄 Frontend shows latest data

## Verify Everything is Working

### Check Service Status
```bash
docker-compose ps
```

All services should be "Up" or "Up (healthy)".

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f api
docker-compose logs -f reddit-scraper-cron
docker-compose logs -f llm-consumer
```

### Test the API
```bash
# Health check
curl http://localhost:8000/health

# Get stats
curl http://localhost:8000/api/v1/stats

# Get job posts (after first scrape)
curl http://localhost:8000/api/v1/job-posts
```

### Test the Frontend
Open http://localhost:3000 in your browser. You should see:
- Title "Reddit Job Posts"
- Search bar
- "Filter by Tags" button
- Message about no jobs (until first scrape runs)

## Trigger Manual Scrape (Optional)

Don't want to wait 2 hours? Run the scraper manually:

```bash
docker-compose exec reddit-scraper-cron python -m src.scraper
```

Watch the logs:
```bash
docker-compose logs -f reddit-scraper-cron
docker-compose logs -f llm-consumer
```

## Check Database Directly

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U reddit_user -d reddit_jobs

# View all job posts
SELECT id, title, cleaned_title, tags FROM raw_job_posts LIMIT 5;

# Count processed vs unprocessed
SELECT
  COUNT(*) FILTER (WHERE processed_at IS NULL) as unprocessed,
  COUNT(*) FILTER (WHERE processed_at IS NOT NULL) as processed
FROM raw_job_posts;

# Exit
\q
```

## Common Issues & Solutions

### "Port already in use"

**Issue**: Port 3000, 8000, 5432, 5672, or 15672 already in use

**Solution**:
```bash
# Find what's using the port (example for 3000)
lsof -i :3000

# Kill the process
kill -9 <PID>

# Or change the port in docker-compose.yml
# For frontend:
ports:
  - "3001:3000"  # Access at localhost:3001
```

### "Container keeps restarting"

**Check logs**:
```bash
docker-compose logs <service-name>
```

**Common fixes**:
- Reddit scraper: Check your Reddit API credentials
- LLM consumer: Ensure you have 8GB+ RAM available
- Database: Check disk space

### "No jobs showing in frontend"

**Possible reasons**:
1. First scrape hasn't run yet (wait up to 2 hours or trigger manually)
2. Reddit API credentials are incorrect
3. Scraper service is failing

**Check**:
```bash
# View scraper logs
docker-compose logs reddit-scraper-cron

# Check database
docker-compose exec postgres psql -U reddit_user -d reddit_jobs \
  -c "SELECT COUNT(*) FROM raw_job_posts;"
```

### "Frontend can't connect to API"

**Verify API is running**:
```bash
curl http://localhost:8000/health
```

**Check frontend logs**:
```bash
docker-compose logs frontend
```

**Verify environment variable**:
```bash
docker-compose exec frontend env | grep API_URL
```

Should show: `NEXT_PUBLIC_API_URL=http://localhost:8000`

## Stopping the System

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (deletes all data!)
docker-compose down -v
```

## Development Mode

### Run Frontend Locally (with hot-reload)
```bash
cd frontend
npm install
npm run dev
```
Access at http://localhost:3000 with instant updates on code changes.

### Run API Locally
```bash
cd api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

## Next Steps

Once everything is running:

1. **Customize the scraping**: Edit `reddit_scraper/src/scraper.py` to add more subreddits
2. **Adjust scraping frequency**: Edit `cron/crontab` to change schedule
3. **Customize tags**: Edit `llm_service/src/analyzer.py` to modify LLM prompt
4. **Style the frontend**: Edit Tailwind classes in `frontend/components/`
5. **Add features**: Extend API with new endpoints in `api/src/main.py`

## Documentation

- **[README.md](README.md)** - Project overview
- **[FRONTEND_SETUP.md](FRONTEND_SETUP.md)** - Frontend development guide
- **[DOCKER_FRONTEND.md](DOCKER_FRONTEND.md)** - Frontend Docker details
- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Docker troubleshooting
- **[GPU_SETUP.md](GPU_SETUP.md)** - GPU acceleration setup

## Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify all services are healthy: `docker-compose ps`
3. Review the documentation links above
4. Check environment variables are set correctly

## System Requirements

**Minimum:**
- 8GB RAM
- 10GB disk space
- Docker 20.10+
- Docker Compose 1.29+

**Recommended:**
- 16GB RAM
- 20GB disk space (for model and data)
- SSD storage
- Multi-core CPU

**For GPU acceleration:**
- NVIDIA GPU with 6GB+ VRAM
- NVIDIA Docker runtime
- See [GPU_SETUP.md](GPU_SETUP.md)

---

**That's it!** You now have a complete job post scraping, analysis, and browsing system running locally. 🚀
