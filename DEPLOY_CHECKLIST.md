# ✅ Deploy Checklist - Nhanh

## 🐳 Backend (Render) - 5 bước

- [ ] **Bước 1**: Đăng ký/Đăng nhập Render.com
- [ ] **Bước 2**: New → Web Service → Connect GitHub
- [ ] **Bước 3**: Cấu hình:
  - Environment: **Docker**
  - Dockerfile Path: `./Dockerfile`
  - Plan: **Free**
- [ ] **Bước 4**: Thêm Environment Variables:
  - `PORT` = `5000`
  - `FLASK_ENV` = `production`
  - `SHOW_BROWSER` = `false`
  - `RECORD_VIDEO` = `false`
- [ ] **Bước 5**: Create Web Service → Chờ build → **Lưu URL backend**

**Backend URL**: `https://____________________.onrender.com`

---

## 🌐 Frontend (Netlify) - 5 bước

- [ ] **Bước 1**: Đăng ký/Đăng nhập Netlify.com
- [ ] **Bước 2**: Add new site → Import from GitHub
- [ ] **Bước 3**: Cấu hình Build:
  - Build command: `npm run build`
  - Publish directory: `dist`
- [ ] **Bước 4**: Thêm Environment Variable:
  - `VITE_API_URL` = `https://your-backend.onrender.com` (URL từ Render)
- [ ] **Bước 5**: Deploy → **Lưu URL frontend**

**Frontend URL**: `https://____________________.netlify.app`

---

## 🔗 Bước cuối: Test

- [ ] Test backend: `curl https://your-backend.onrender.com/health`
- [ ] Test frontend: Mở URL Netlify → Xem có hoạt động không
- [ ] Test chat: Gửi tin nhắn → Xem có phản hồi không

---

## ⚠️ Lưu ý quan trọng

1. **Backend URL phải được set trong Frontend**:
   - Trên Netlify: Environment Variable `VITE_API_URL`
   - Sau khi set, phải **trigger rebuild**

2. **Render Free Tier**:
   - Spins down sau 15 phút không dùng
   - Lần đầu wake up mất ~30 giây
   - Có thể dùng UptimeRobot để ping mỗi 5 phút

3. **Tự động deploy**:
   - Render: Tự động deploy khi push code
   - Netlify: Tự động deploy khi push code

---

## 📚 Xem hướng dẫn chi tiết

Xem file `DEPLOY_GUIDE.md` để có hướng dẫn từng bước chi tiết với hình ảnh.

