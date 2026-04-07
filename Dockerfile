FROM python:3.11-slim

# Install system dependencies for lxml, pdfplumber, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libxml2-dev libxslt-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create runtime directories
RUN mkdir -p data/files data/db logs

CMD ["python", "run.py"]
