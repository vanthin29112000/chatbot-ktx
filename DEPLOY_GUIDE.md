# 🚀 Hướng Dẫn Deploy - Backend (Render) + Frontend (Netlify)

## 📋 Tổng quan

- **Backend**: Deploy lên Render.com (Free tier)
- **Frontend**: Deploy lên Netlify (Free tier)
- **Tự động deploy**: Từ GitHub repository

---

## 🔧 Bước 1: Chuẩn bị GitHub Repository

### 1.1. Đảm bảo code đã được commit và push lên GitHub

```bash
# Kiểm tra git status
git status

# Nếu có thay đổi, commit và push
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 1.2. Đảm bảo các file cần thiết đã có:

✅ `Dockerfile` - Cho backend
✅ `render.yaml` - Cấu hình Render (tùy chọn)
✅ `netlify.toml` - Cấu hình Netlify
✅ `requirements.txt` - Python dependencies
✅ `package.json` - Node.js dependencies

---

## 🐳 Bước 2: Deploy Backend lên Render

### 2.1. Đăng ký/Đăng nhập Render

1. Truy cập: https://render.com
2. Đăng ký/Đăng nhập bằng GitHub account
3. Xác nhận email (nếu cần)

### 2.2. Tạo Web Service mới

1. Click **"New +"** → Chọn **"Web Service"**
2. **Connect GitHub repository**:
   - Chọn repository của bạn
   - Click **"Connect"**

### 2.3. Cấu hình Web Service

**Basic Settings:**
- **Name**: `chatbot-backend` (hoặc tên bạn muốn)
- **Region**: Chọn gần bạn nhất (Singapore, US, etc.)
- **Branch**: `main` (hoặc branch bạn muốn deploy)
- **Root Directory**: Để trống (hoặc `./` nếu cần)

**Build & Deploy:**
- **Environment**: Chọn **"Docker"**
- **Dockerfile Path**: `./Dockerfile` (hoặc để mặc định)
- **Docker Build Context**: Để trống (hoặc `./`)

**Advanced Settings:**
- **Auto-Deploy**: `Yes` (tự động deploy khi push code)

### 2.4. Thêm Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**:

| Key | Value | Mô tả |
|-----|-------|-------|
| `PORT` | `5000` | Port của Flask app |
| `FLASK_ENV` | `production` | Môi trường production |
| `SHOW_BROWSER` | `false` | Ẩn browser (headless) |
| `RECORD_VIDEO` | `false` | Không ghi video |

### 2.5. Chọn Plan

- **Free Plan**: 750 giờ/tháng (đủ cho 24/7)
- Click **"Create Web Service"**

### 2.6. Chờ Build

- Build sẽ mất **5-10 phút** lần đầu
- Bạn có thể xem logs trong tab **"Logs"**
- Khi build xong, bạn sẽ có URL: `https://your-app.onrender.com`

### 2.7. Test Backend

```bash
# Test health endpoint
curl https://your-app.onrender.com/health

# Phải trả về: {"status": "ok"}
```

**Lưu URL backend này lại!** (Ví dụ: `https://chatbot-backend-abc123.onrender.com`)

---

## 🌐 Bước 3: Deploy Frontend lên Netlify

### 3.1. Đăng ký/Đăng nhập Netlify

1. Truy cập: https://netlify.com
2. Đăng ký/Đăng nhập bằng GitHub account
3. Xác nhận email (nếu cần)

### 3.2. Tạo Site mới

1. Click **"Add new site"** → **"Import an existing project"**
2. Chọn **"Deploy with GitHub"**
3. **Authorize Netlify** để truy cập GitHub
4. Chọn repository của bạn

### 3.3. Cấu hình Build Settings

**Build settings:**
- **Base directory**: Để trống
- **Build command**: `npm run build`
- **Publish directory**: `dist`

**Advanced build settings:**
- Click **"Show advanced"** → **"New variable"**

### 3.4. Thêm Environment Variables

Thêm biến môi trường quan trọng:

| Key | Value | Mô tả |
|-----|-------|-------|
| `VITE_API_URL` | `https://your-app.onrender.com` | **URL backend trên Render** (thay bằng URL thực tế) |

**⚠️ QUAN TRỌNG**: Thay `your-app.onrender.com` bằng URL backend thực tế từ Render!

### 3.5. Deploy

1. Click **"Deploy site"**
2. Chờ build (2-5 phút)
3. Khi xong, bạn sẽ có URL: `https://random-name-123.netlify.app`

### 3.6. Đổi tên Site (Tùy chọn)

1. Vào **"Site settings"** → **"Change site name"**
2. Đổi thành tên bạn muốn (ví dụ: `chatbot-ktx`)
3. URL mới: `https://chatbot-ktx.netlify.app`

---

## 🔗 Bước 4: Cập nhật Frontend với Backend URL

### 4.1. Cập nhật Environment Variable trên Netlify

1. Vào **"Site settings"** → **"Environment variables"**
2. Tìm `VITE_API_URL`
3. Click **"Edit"**
4. Cập nhật URL backend từ Render
5. Click **"Save"**

### 4.2. Trigger Rebuild

1. Vào **"Deploys"** tab
2. Click **"Trigger deploy"** → **"Clear cache and deploy site"**
3. Chờ rebuild xong

---

## ✅ Bước 5: Test Deployment

### 5.1. Test Backend

```bash
# Test health
curl https://your-backend.onrender.com/health

# Test capture status
curl https://your-backend.onrender.com/api/capture-status
```

### 5.2. Test Frontend

1. Mở URL Netlify: `https://your-site.netlify.app`
2. Mở DevTools (F12) → **Console** tab
3. Xem logs:
   - `🚀 Bắt đầu capture payload ngay lập tức...`
   - `✅ Auto capture started, waiting for result...`
   - `✅ Đã tự động capture và lưu payload thành công!`

### 5.3. Test Chat

1. Nhập tin nhắn vào ô chat
2. Gửi tin nhắn
3. Xem có phản hồi từ chatbot không

---

## 🔄 Bước 6: Tự động Deploy (Đã được bật)

### Render:
- ✅ Tự động deploy khi push code lên GitHub
- ✅ Có thể tắt trong Settings → Auto-Deploy

### Netlify:
- ✅ Tự động deploy khi push code lên GitHub
- ✅ Có thể tắt trong Site settings → Build & deploy → Continuous Deployment

---

## 🐛 Troubleshooting

### Backend không chạy?

1. **Kiểm tra logs trên Render:**
   - Vào **"Logs"** tab
   - Xem có lỗi gì không

2. **Kiểm tra Playwright:**
   - Logs sẽ hiện: `⚠️  Không thể cài browser trong build, sẽ cài khi chạy`
   - Đây là bình thường, Playwright sẽ tự download khi chạy

3. **Kiểm tra Port:**
   - Đảm bảo `PORT=5000` trong Environment Variables

### Frontend không kết nối được Backend?

1. **Kiểm tra CORS:**
   - Backend đã có `CORS(app)` → Cho phép tất cả origins
   - Nếu vẫn lỗi, kiểm tra logs backend

2. **Kiểm tra Environment Variable:**
   - Đảm bảo `VITE_API_URL` đã được set trên Netlify
   - URL phải đúng (có `https://`, không có trailing slash)

3. **Kiểm tra Network:**
   - Mở DevTools → Network tab
   - Xem có request đến backend không
   - Xem có lỗi CORS không

### Build fail trên Render?

1. **Kiểm tra Dockerfile:**
   - Đảm bảo `Dockerfile` có trong root directory
   - Đảm bảo `requirements.txt` có đầy đủ dependencies

2. **Kiểm tra logs:**
   - Xem logs để biết lỗi cụ thể
   - Thường là thiếu dependencies hoặc lỗi syntax

### Build fail trên Netlify?

1. **Kiểm tra Build command:**
   - Phải là: `npm run build`
   - Publish directory: `dist`

2. **Kiểm tra Node version:**
   - Netlify sẽ tự động detect từ `package.json`
   - Hoặc set trong `netlify.toml`: `NODE_VERSION = "18"`

---

## 📝 Checklist Deploy

### Trước khi deploy:
- [ ] Code đã được commit và push lên GitHub
- [ ] Đã test local (backend và frontend)
- [ ] `Dockerfile` đã có
- [ ] `netlify.toml` đã có
- [ ] `requirements.txt` đã có đầy đủ dependencies

### Sau khi deploy Backend:
- [ ] Backend URL đã có (từ Render)
- [ ] Test `/health` endpoint thành công
- [ ] Test `/api/capture-status` thành công

### Sau khi deploy Frontend:
- [ ] Frontend URL đã có (từ Netlify)
- [ ] Đã set `VITE_API_URL` trên Netlify
- [ ] Đã trigger rebuild sau khi set environment variable
- [ ] Test frontend có kết nối được backend không

---

## 🎯 Kết quả mong đợi

Sau khi deploy xong:

1. ✅ Backend chạy trên Render: `https://your-backend.onrender.com`
2. ✅ Frontend chạy trên Netlify: `https://your-site.netlify.app`
3. ✅ Frontend tự động lấy payload từ backend
4. ✅ Chatbot hoạt động bình thường
5. ✅ Tự động deploy khi push code mới

---

## 💡 Tips

### Render Free Tier:
- ⚠️ Spins down sau 15 phút không dùng
- ⚠️ Wake up mất ~30 giây
- 💡 Giải pháp: Dùng [UptimeRobot](https://uptimerobot.com) (free) để ping mỗi 5 phút

### Netlify Free Tier:
- ✅ Không giới hạn bandwidth
- ✅ Tự động SSL
- ✅ CDN toàn cầu
- ✅ Không spins down

### Tối ưu:
- Backend: Dùng keep-alive endpoint để tránh spin down
- Frontend: Build production với `npm run build` (đã tự động)

---

## 📞 Hỗ trợ

Nếu gặp vấn đề:
1. Kiểm tra logs trên Render/Netlify
2. Kiểm tra DevTools Console trên browser
3. Test API endpoints trực tiếp bằng curl/Postman
4. Xem các file hướng dẫn khác trong project

---

**Chúc bạn deploy thành công! 🎉**

