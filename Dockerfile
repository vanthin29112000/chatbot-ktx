# Dùng python:3.11 (không phải slim) - đã có nhiều dependencies sẵn
# Đơn giản hơn nhiều so với slim + cài thủ công
FROM python:3.11

WORKDIR /app

# Copy và cài Python dependencies
# Dùng requirements.backend.txt để Netlify không detect Python
COPY requirements.backend.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Cài system dependencies cho Playwright Chromium
# Bỏ qua playwright install-deps vì nó cố cài fonts không có sẵn (ttf-ubuntu-font-family, ttf-unifont)
# Cài thủ công các dependencies cần thiết
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-liberation \
    fonts-dejavu-core \
    fontconfig \
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
    libgconf-2-4 \
    libcairo-gobject2 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    && rm -rf /var/lib/apt/lists/*

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
