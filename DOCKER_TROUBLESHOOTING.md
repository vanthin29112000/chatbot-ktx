# 🔧 Docker Troubleshooting cho Render

## Lỗi: exit code 127

### Nguyên nhân:
- `apt-key` đã deprecated trong Debian/Ubuntu mới
- GPG key không được thêm đúng cách

### Giải pháp đã áp dụng:
✅ Đã sửa Dockerfile để dùng `gpg --dearmor` thay vì `apt-key`
✅ Tách thành nhiều RUN commands để dễ debug

---

## Nếu vẫn lỗi, thử các cách sau:

### Cách 1: Dùng Dockerfile hiện tại (đã sửa)

1. **Commit và push:**
```bash
git add Dockerfile
git commit -m "Fix: Update Dockerfile for newer Debian"
git push
```

2. **Trên Render:**
   - Vào service → Settings → Manual Deploy → Clear build cache & deploy

### Cách 2: Dùng Chromium thay vì Chrome

1. **Đổi tên file:**
```bash
# Rename Dockerfile.chromium thành Dockerfile
mv Dockerfile Dockerfile.chrome.backup
mv Dockerfile.chromium Dockerfile
```

2. **Cập nhật payload_capture_server.py để hỗ trợ Chromium:**
   - Thêm option để dùng chromium nếu không tìm thấy chrome

3. **Commit và push:**
```bash
git add Dockerfile payload_capture_server.py
git commit -m "Use Chromium instead of Chrome"
git push
```

### Cách 3: Dùng base image khác

Thử dùng `python:3.11` thay vì `python:3.11-slim`:

```dockerfile
FROM python:3.11

# ... rest of Dockerfile
```

### Cách 4: Build local để test

```bash
# Build image
docker build -t chatbot-test .

# Test chạy
docker run -p 5000:5000 chatbot-test

# Nếu build thành công local nhưng fail trên Render:
# - Kiểm tra logs trên Render
# - So sánh với local
```

---

## Kiểm tra logs trên Render

1. Vào Render dashboard
2. Chọn service
3. Click "Logs" tab
4. Xem lỗi chi tiết ở đâu

---

## Các lỗi thường gặp:

### 1. "apt-get: command not found"
- **Nguyên nhân**: Base image không có apt
- **Giải pháp**: Dùng `python:3.11` thay vì `python:3.11-slim`

### 2. "gpg: command not found"
- **Nguyên nhân**: Chưa cài gnupg
- **Giải pháp**: Đảm bảo có `gnupg` trong apt-get install

### 3. "Chrome not found"
- **Nguyên nhân**: Chrome chưa cài hoặc path sai
- **Giải pháp**: 
  - Kiểm tra `google-chrome-stable` đã cài chưa
  - Thêm: `chrome_options.binary_location = "/usr/bin/google-chrome-stable"`

### 4. "Out of memory"
- **Nguyên nhân**: Free tier chỉ có 512MB RAM
- **Giải pháp**: 
  - Tối ưu Dockerfile (xóa cache sau mỗi bước)
  - Upgrade plan hoặc dùng VPS

---

## Dockerfile tối ưu (đã test)

```dockerfile
FROM python:3.11-slim

# Cài dependencies cơ bản
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Thêm Chrome repo
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | \
    gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > \
    /etc/apt/sources.list.d/google-chrome.list

# Cài Chrome và dependencies
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
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
    lsb-release \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "payload_capture_server.py"]
```

---

## Test local trước khi deploy

```bash
# Build
docker build -t chatbot .

# Run
docker run -p 5000:5000 chatbot

# Test API
curl http://localhost:5000/health
```

Nếu test local thành công nhưng fail trên Render → Kiểm tra:
- Environment variables
- Build settings
- Resource limits

