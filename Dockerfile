# Dùng python:3.11 (không phải slim) - đã có nhiều dependencies sẵn
# Đơn giản hơn nhiều so với slim + cài thủ công
FROM python:3.11

WORKDIR /app

# Copy và cài Python dependencies
# Dùng requirements.backend.txt để Netlify không detect Python
COPY requirements.backend.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Cài fonts tương đương trước (để tránh lỗi khi install-deps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-liberation \
    fonts-dejavu-core \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Cài Playwright Chromium
# Bỏ qua install-deps vì nó cố cài fonts không có (ttf-ubuntu-font-family, ttf-unifont)
# python:3.11 đã có đủ dependencies, chỉ cần browser
RUN playwright install chromium

# Copy code
COPY . .

# Expose port
EXPOSE 5000

# Set Python to unbuffered mode để logs hiển thị ngay
ENV PYTHONUNBUFFERED=1

# Chạy app
CMD ["python", "payload_capture_server.py"]
