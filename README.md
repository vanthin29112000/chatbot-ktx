# 💬 Chatbot Application

Ứng dụng chatbot với React frontend và Flask backend, tự động capture payload từ Zapier chatbot.

## 🚀 Cài đặt và Chạy

### Frontend (React)

```bash
npm install
npm run dev
```

Frontend chạy tại: `http://localhost:5173`

### Backend (Flask + Playwright)

```bash
pip install -r requirements.backend.txt
python payload_capture_server.py
```

Backend chạy tại: `http://localhost:5000`

### Với Docker

```bash
docker build -t chatbot-app .
docker run -p 5000:5000 chatbot-app
```

## 🌐 Deploy

### Frontend (Netlify)

1. Kết nối repository với Netlify
2. Build command: `npm run build`
3. Publish directory: `dist`
4. Environment variables:
   - `VITE_API_URL`: URL backend (ví dụ: `https://your-backend.onrender.com`)

### Backend (Render)

1. Tạo Web Service mới trên Render
2. Kết nối repository
3. Build command: `pip install -r requirements.backend.txt && playwright install chromium && playwright install-deps chromium`
4. Start command: `python payload_capture_server.py`
5. Environment variables:
   - `PORT`: 5000 (tự động set bởi Render)
   - `FLASK_ENV`: `production`
   - `SHOW_BROWSER`: `false` (optional, để hiển thị browser khi debug)
   - `RECORD_VIDEO`: `false` (optional, để ghi video khi debug)

## 📋 Tính năng

- ✅ Popup thu thập thông tin sinh viên (tên, phòng KTX hoặc số điện thoại)
- ✅ Tự động capture payload từ Zapier chatbot (sử dụng Playwright)
- ✅ Chat với chatbot (streaming responses)
- ✅ Đánh giá và feedback
- ✅ Loading screen khi capture payload
- ✅ Responsive design

## 🔧 Environment Variables

### Frontend
- `VITE_API_URL`: URL của backend API (mặc định: `http://localhost:5000`)

### Backend
- `PORT`: Port để chạy server (mặc định: 5000)
- `FLASK_ENV`: `production` hoặc `development`
- `SHOW_BROWSER`: `true`/`false` - Hiển thị browser khi capture (debug)
- `RECORD_VIDEO`: `true`/`false` - Ghi video khi capture (debug)

## 📁 Cấu trúc Project

```
.
├── src/                    # React frontend
│   ├── App.jsx            # Component chính
│   └── App.css            # Styles
├── payload_capture_server.py  # Flask backend
├── Dockerfile             # Docker config
├── requirements.backend.txt   # Python dependencies
├── package.json           # Node dependencies
└── README.md             # File này
```

## 🛠️ Tech Stack

- **Frontend**: React + Vite + ReactMarkdown
- **Backend**: Flask + Playwright + Requests
- **Deploy**: Netlify (Frontend) + Render (Backend)

## 📝 API Endpoints

### Backend

- `GET /health` - Health check
- `POST /api/capture-payload` - Bắt đầu capture payload
- `GET /api/capture-status` - Kiểm tra trạng thái capture
- `GET /api/get-payload` - Lấy payload đã capture
- `POST /api/reset-capture` - Reset capture flag
- `POST /api/chat` - Proxy request đến Zapier chatbot (tránh CORS)

## ⚠️ Troubleshooting

### Backend không capture được payload

1. Kiểm tra Playwright dependencies đã được cài trong Dockerfile
2. Kiểm tra logs để xem có lỗi gì không
3. Thử set `SHOW_BROWSER=true` để xem browser có chạy không

### CORS errors

- Đảm bảo backend có CORS enabled (đã có trong code)
- Kiểm tra `VITE_API_URL` trong frontend đúng với backend URL

### Browser không launch

- Rebuild Docker image với Dockerfile mới (đã cài đầy đủ dependencies)
- Kiểm tra logs để xem lỗi cụ thể

## 📄 License

MIT
