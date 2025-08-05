FROM --platform=linux/amd64 python:3.11-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    REDIS_HOST=localhost \
    REDIS_PORT=6379 \
    REDIS_DB=0

# Set working directory
WORKDIR /app

# -----------------------------------------------------------------------------
# Install system dependencies (Chrome, Redis, Supervisor, etc.)
# -----------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libnss3 \
    libxshmfence1 \
    libglu1-mesa \
    redis-server \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install additional fonts (Arabic, Emoji) for proper rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-noto \
    fonts-noto-color-emoji \
    fonts-dejavu-core \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Install Google Chrome & ChromeDriver (for Selenium part of the app)
# -----------------------------------------------------------------------------
RUN wget -q -O google-chrome-stable_current_amd64.deb \
        https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get update && apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    fonts-liberation \
    fonts-dejavu \
    pulseaudio

# Update font cache after installing fonts
RUN fc-cache -fv

# Install ChromeDriver matching the installed Chrome version (robust for slim images)
RUN set -e; \
    CHROME_VERSION=$(google-chrome --version | awk '{print $3}') && \
    MAJOR_VERSION="${CHROME_VERSION%%.*}" && \
    CHROMEDRIVER_VERSION=$(curl -fsSL "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${MAJOR_VERSION}") && \
    echo "Installing ChromeDriver version ${CHROMEDRIVER_VERSION} for Chrome ${CHROME_VERSION}"; \
    wget -q "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip && \
    unzip -qq /tmp/chromedriver.zip -d /tmp && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver*

# -----------------------------------------------------------------------------
# Python dependencies
# -----------------------------------------------------------------------------
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for SQLite database persistence
RUN mkdir -p /app/data

# -----------------------------------------------------------------------------
# Supervisor configuration - run Redis + API + Worker + Webhook in one container
# -----------------------------------------------------------------------------
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose ports (API: 8000, Webhook: 8001, Redis: 6379, RQ Dashboard: 9181)
EXPOSE 8000 8001 6379 9181

# Default command: start Supervisor
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
