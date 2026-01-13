FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for lxml and arelle
RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Expose port
EXPOSE 3008

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "3008"]
