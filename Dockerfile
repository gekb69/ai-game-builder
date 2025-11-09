FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p data logs backups models reports/security

# Download NLTK data
RUN python -m nltk.downloader punkt stopwords wordnet

# Expose ports
EXPOSE 8080 8081 8082

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Start script
COPY docker-start.sh /app/docker-start.sh
RUN chmod +x /app/docker-start.sh

CMD ["./docker-start.sh"]
