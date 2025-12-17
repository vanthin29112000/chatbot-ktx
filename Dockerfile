FROM python:3.11-slim

# Cài đặt system dependencies cho Playwright Chromium
# Bao gồm tất cả các thư viện cần thiết để chạy Chromium headless
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    fonts-liberation \
    # Playwright Chromium dependencies
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
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copy và cài Python dependencies
# Dùng requirements.backend.txt để Netlify không detect Python
COPY requirements.backend.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Cài Playwright Chromium trong build để tránh phải tải lại mỗi lần
# Browser sẽ được cache trong Docker image
# Lưu ý: install-deps có thể fail nếu deps đã được cài thủ công ở trên, nhưng không sao
RUN playwright install chromium && \
    (playwright install-deps chromium || echo "Note: System deps may already be installed manually")

# Copy code
COPY . .

# Expose port
EXPOSE 5000

# Set Python to unbuffered mode để logs hiển thị ngay
ENV PYTHONUNBUFFERED=1

# Chạy app
CMD ["python", "payload_capture_server.py"]
