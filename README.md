# 💬 Chatbot Application

Ứng dụng chatbot với React frontend và Flask backend, tự động capture payload từ Zapier chatbot.

## 🚀 Quick Start

### Local Development

#### Frontend:
```bash
npm install
npm run dev
```

#### Backend:
```bash
pip install -r requirements.txt
python payload_capture_server.py
```

## 📦 Deploy

### Frontend → Netlify
- Xem file `GITHUB_DEPLOY.md` hoặc `QUICK_START.md`

### Backend → Render
- Xem file `GITHUB_DEPLOY.md` hoặc `BACKEND_DEPLOY_COMPARISON.md`

## 📚 Documentation

- `GITHUB_DEPLOY.md` - Hướng dẫn deploy chi tiết
- `QUICK_START.md` - Hướng dẫn nhanh
- `BACKEND_DEPLOY_COMPARISON.md` - So sánh các dịch vụ backend
- `DEPLOY.md` - Tổng quan về deployment

## 🛠️ Tech Stack

- **Frontend**: React + Vite
- **Backend**: Flask + Selenium
- **Deploy**: Netlify (Frontend) + Render (Backend)

## 📝 Features

- ✅ Popup thu thập thông tin sinh viên
- ✅ Tự động capture payload từ Zapier
- ✅ Chat với chatbot
- ✅ Đánh giá và feedback
- ✅ Responsive design

## 🔧 Environment Variables

### Frontend:
- `VITE_API_URL`: URL của backend API

### Backend:
- `PORT`: Port để chạy server (mặc định: 5000)
- `FLASK_ENV`: `production` hoặc `development`

## 📄 License

MIT
