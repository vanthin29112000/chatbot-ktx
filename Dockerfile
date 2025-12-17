FROM python:3.11-slim

# Cài đặt dependencies cơ bản
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copy và cài Python dependencies
# Dùng requirements.backend.txt để Netlify không detect Python
COPY requirements.backend.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Cài Playwright Chromium và system dependencies
# playwright install-deps sẽ tự động cài đúng dependencies cho hệ thống
# Cần apt-get update lại vì install-deps có thể cần cài thêm packages
RUN apt-get update && \
    playwright install chromium && \
    playwright install-deps chromium && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Copy code
COPY . .

# Expose port
EXPOSE 5000

# Set Python to unbuffered mode để logs hiển thị ngay
ENV PYTHONUNBUFFERED=1

# Chạy app
CMD ["python", "payload_capture_server.py"]
