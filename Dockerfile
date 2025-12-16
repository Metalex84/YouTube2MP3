# YouTube to MP3 Downloader - Docker Container (Web Interface)
FROM python:3.11-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-alpine

# Install runtime dependencies only
RUN apk add --no-cache \
    ffmpeg \
    && rm -rf /var/cache/apk/*

# Set working directory
WORKDIR /app

# Copy Python packages from builder to system location
COPY --from=builder /root/.local /usr/local

# Copy only necessary application files
COPY app.py .
COPY descargar_audio.py .
COPY templates/ templates/
COPY static/ static/

# Create directories for downloads and logs
RUN mkdir -p /app/downloads /app/logs

# Configure environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV DOWNLOAD_DIR=/app/downloads
ENV LOGS_DIR=/app/logs

# Non-root user for security
RUN adduser -D -g '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port for web application
EXPOSE 5000

# Entry point for Flask web application
CMD ["python", "app.py"]
