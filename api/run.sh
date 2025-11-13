#!/bin/bash

# Script to run the API locally

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run the API with uvicorn
echo "Starting Reddit Job Posts API..."
echo "API will be available at: http://${API_HOST:-0.0.0.0}:${API_PORT:-8000}"
echo "API docs available at: http://localhost:${API_PORT:-8000}/docs"

uvicorn src.main:app --host ${API_HOST:-0.0.0.0} --port ${API_PORT:-8000} --reload
