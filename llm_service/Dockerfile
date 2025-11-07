# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies including curl for Ollama
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Add src to Python path
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Create entrypoint script with GPU detection
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Check for GPU\n\
if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null; then\n\
    echo "GPU detected! Ollama will use GPU acceleration."\n\
    export OLLAMA_GPU=1\n\
else\n\
    echo "No GPU detected. Ollama will use CPU (slower but works)."\n\
    export OLLAMA_GPU=0\n\
fi\n\
\n\
echo "Starting Ollama service..."\n\
ollama serve &\n\
OLLAMA_PID=$!\n\
\n\
echo "Waiting for Ollama to be ready..."\n\
sleep 5\n\
\n\
echo "Pulling Ollama model: ${OLLAMA_MODEL:-llama3.1:8b}"\n\
ollama pull ${OLLAMA_MODEL:-llama3.1:8b}\n\
\n\
echo "Starting consumer..."\n\
python src/consumer.py\n\
\n\
# Cleanup\n\
kill $OLLAMA_PID 2>/dev/null || true\n\
' > /entrypoint.sh && chmod +x /entrypoint.sh

# Run the consumer
CMD ["/entrypoint.sh"]
