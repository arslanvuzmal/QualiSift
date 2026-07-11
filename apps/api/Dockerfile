FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project metadata + package source needed to build/install the package.
COPY pyproject.toml ./
COPY app ./app

# Install Python dependencies (and the app package itself).
RUN pip install --no-cache-dir ".[dev]"

# Copy the rest of the application code (alembic, scripts, templates, ...).
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
