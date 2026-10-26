# Multi-stage secure Dockerfile for ClipMind AI
FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install essential runtime OS dependencies for OpenCV, PIL, and FFmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root application user and group
RUN groupadd -r clipmind && useradd -r -g clipmind -u 10001 -m -d /home/clipmind clipmind

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY clipmind/ ./clipmind/
COPY app.py .
COPY README.md .

# Create temporary working directory and set ownership to non-root user
RUN mkdir -p /app/.clipmind_tmp && \
    chown -R clipmind:clipmind /app /home/clipmind

# Switch to non-root user
USER clipmind

# Expose standard Streamlit port
EXPOSE 8501

# Healthcheck to monitor service responsiveness
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Launch Streamlit server
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--browser.gatherUsageStats=false"]
