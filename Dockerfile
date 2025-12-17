FROM python:3.11-slim

# Tối ưu: Cài đặt tất cả dependencies trong một layer để cache tốt hơn
# Sử dụng Chromium thay vì Chrome (nhẹ hơn, cài nhanh hơn)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Dependencies cho Chromium
    chromium \
    chromium-driver \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    # Cleanup trong cùng layer để giảm image size
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Tối ưu: Copy requirements.txt trước để tận dụng Docker layer caching
# Nếu requirements.txt không đổi, sẽ không cần cài lại pip packages
COPY requirements.txt .

# Cài Python dependencies với cache
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy code sau cùng (code thay đổi thường xuyên nhất)
COPY . .

# Expose port
EXPOSE 5000

# Chạy app
CMD ["python", "payload_capture_server.py"]

