FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml README.md ./
COPY secblast/ ./secblast/

RUN pip install --no-cache-dir -e ".[dev]"

# Default command - run Python shell
CMD ["python"]
