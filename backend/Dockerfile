FROM python:3.12-slim

WORKDIR /app

# Install system dependencies required by asyncpg and Playwright
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium browser and its OS dependencies
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application source
COPY . .

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
