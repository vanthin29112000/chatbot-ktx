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
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Không cài browser trong build - Playwright sẽ tự động download khi chạy lần đầu
# Điều này giúp build nhanh hơn và tránh lỗi
# Browser sẽ được download tự động khi container chạy lần đầu

# Copy code
COPY . .

# Expose port
EXPOSE 5000

# Chạy app
CMD ["python", "payload_capture_server.py"]
