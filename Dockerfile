# Dùng python:3.11-slim để giảm kích thước image
FROM python:3.11-slim

WORKDIR /app

# Cài system dependencies cho Playwright Chromium (headless mode)
# Chỉ cài các package thực sự cần thiết để Chromium chạy headless
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-liberation \
    fonts-dejavu-core \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libx11-xcb1 \
    libxcursor1 \
    libxi6 \
    libxtst6 \
    && rm -rf /var/lib/apt/lists/*

# Copy và cài Python dependencies trước
COPY requirements.backend.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Cài Playwright Chromium (không cài install-deps vì đã cài thủ công ở trên)
RUN playwright install chromium

# Copy code
COPY . .

# Expose port
EXPOSE 5000

# Set Python to unbuffered mode để logs hiển thị ngay
ENV PYTHONUNBUFFERED=1

# Chạy app
CMD ["python", "payload_capture_server.py"]
