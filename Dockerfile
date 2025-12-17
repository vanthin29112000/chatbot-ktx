FROM python:3.11-slim

# Cài đặt dependencies cơ bản cho Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Dependencies cho Playwright
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libatspi2.0-0 \
    libxshmfence1 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxext6 \
    libxrender1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libpango-1.0-0 \
    libcairo2 \
    libfontconfig1 \
    libgdk-pixbuf2.0-0 \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copy và cài Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Cài đặt Playwright browser (với error handling)
# Nếu fail, sẽ để Playwright tự động download khi chạy
RUN playwright install chromium || echo "⚠️  Không thể cài browser trong build, sẽ cài khi chạy"

# Copy code
COPY . .

# Expose port
EXPOSE 5000

# Chạy app
CMD ["python", "payload_capture_server.py"]
