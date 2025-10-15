# Use an official lightweight Python runtime as a parent image
FROM python:3.14-64

# Prevent Python from writing .pyc files and enable stdout/stderr flushing
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Install build dependencies (kept minimal)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker layer caching)
COPY requirements.txt /app/requirements.txt

# Install Python deps
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app

# Create a non-root user and set permissions
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app

USER appuser

# Expose port (Render provides $PORT at runtime; default fallback 5000)
EXPOSE 5000

# Use gunicorn and bind to $PORT environment variable provided by Render
CMD ["sh", "-c", "exec gunicorn app_with_predict:app -w 4 -k gthread -b 0.0.0.0:${PORT:-5000} --timeout 60"]
