# Hướng dẫn Deploy Project Chatbot

## Tổng quan

Project này gồm 2 phần:
- **Frontend**: React + Vite (static files)
- **Backend**: Flask server với Selenium (cần server có Chrome/ChromeDriver)

## Phương án 1: Deploy riêng biệt (Khuyến nghị)

### Frontend → Vercel/Netlify
### Backend → Railway/Render/Heroku

---

## Phương án 2: Deploy trên VPS (Full control)

### Yêu cầu:
- VPS với Ubuntu/Debian
- Node.js và Python đã cài
- Chrome/ChromeDriver

---

## Chi tiết từng phương án

### 🚀 Phương án 1A: Vercel (Frontend) + Railway (Backend)

#### Deploy Frontend lên Vercel:

1. **Build project:**
```bash
npm run build
```

2. **Tạo file `vercel.json`:**
```json
{
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

3. **Deploy:**
   - Push code lên GitHub
   - Kết nối repo với Vercel
   - Thêm environment variable: `VITE_API_URL=https://your-backend-url.com`

#### Deploy Backend lên Railway:

1. **Tạo file `Procfile`:**
```
web: python payload_capture_server.py
```

2. **Cập nhật `payload_capture_server.py`:**
   - Sử dụng `os.environ.get('PORT', 5000)` cho port
   - Thêm Chrome dependencies

3. **Deploy:**
   - Push code lên GitHub
   - Kết nối repo với Railway
   - Railway tự động detect Python và cài dependencies

---

### 🚀 Phương án 1B: Netlify (Frontend) + Render (Backend)

#### Deploy Frontend lên Netlify:

1. **Tạo file `netlify.toml`:**
```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

2. **Deploy:**
   - Push code lên GitHub
   - Kết nối repo với Netlify
   - Thêm environment variable: `VITE_API_URL=https://your-backend-url.com`

#### Deploy Backend lên Render:

1. **Tạo file `render.yaml`:**
```yaml
services:
  - type: web
    name: chatbot-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python payload_capture_server.py
    envVars:
      - key: PORT
        value: 5000
```

2. **Deploy:**
   - Push code lên GitHub
   - Kết nối repo với Render
   - Render sẽ tự động deploy

---

### 🖥️ Phương án 2: Deploy trên VPS

#### Setup VPS:

1. **Cài đặt dependencies:**
```bash
# Cài Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Cài Python và pip
sudo apt-get install python3 python3-pip

# Cài Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# Cài ChromeDriver
sudo apt-get install -y chromium-chromedriver
```

2. **Setup project:**
```bash
# Clone project
git clone <your-repo>
cd test-chat-bot

# Cài frontend dependencies
npm install

# Build frontend
npm run build

# Cài backend dependencies
pip install -r requirements.txt
```

3. **Chạy với PM2 (process manager):**
```bash
# Cài PM2
sudo npm install -g pm2

# Chạy backend
pm2 start payload_capture_server.py --interpreter python3 --name chatbot-backend

# Serve frontend (dùng serve hoặc nginx)
npm install -g serve
pm2 serve dist 3000 --name chatbot-frontend --spa
```

4. **Setup Nginx (tùy chọn):**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /path/to/project/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Environment Variables cần thiết

### Frontend:
- `VITE_API_URL`: URL của backend API (ví dụ: `https://your-backend.railway.app`)

### Backend:
- `PORT`: Port để chạy server (mặc định: 5000)
- `FLASK_ENV`: `production` hoặc `development`

---

## Lưu ý quan trọng

1. **Selenium trên server:**
   - Cần Chrome/ChromeDriver trên server
   - Railway/Render có thể cần buildpack đặc biệt
   - VPS là lựa chọn tốt nhất cho Selenium

2. **CORS:**
   - Đảm bảo backend cho phép domain frontend
   - Đã có `CORS(app)` trong code

3. **API URL:**
   - Cần cập nhật hardcode `localhost:5000` thành environment variable
   - Xem file `.env.example`

4. **Security:**
   - Không commit `.env` files
   - Sử dụng HTTPS cho production
   - Rate limiting cho API endpoints

---

## Troubleshooting

### Backend không chạy được Selenium:
- Kiểm tra Chrome/ChromeDriver đã cài
- Thử dùng `--headless` mode
- Kiểm tra dependencies trong `requirements.txt`

### Frontend không kết nối được Backend:
- Kiểm tra CORS settings
- Kiểm tra API URL trong environment variables
- Kiểm tra network requests trong browser console

