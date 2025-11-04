# Job Post Analyzer Service

This service provides an API for analyzing job posts using OpenAI's GPT model to extract structured information.

## Setup

1. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Set up your OpenAI API key in the `.env` file:
```
OPENAI_API_KEY=your_api_key_here
```

## Running the Service

Start the FastAPI server:
```bash
uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST /analyze
Analyzes a job post and extracts structured information.

Request body:
```json
{
    "title": "string",
    "body": "string",
    "subreddit": "string",
    "url": "string",
    "created_utc": "string"
}
```

### GET /health
Health check endpoint.

## Documentation

- API documentation: `http://localhost:8000/docs`
- OpenAPI specification: `http://localhost:8000/openapi.json`