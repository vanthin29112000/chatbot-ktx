# 🚀 Hướng dẫn Deploy Frontend lên Netlify

## 📋 Bước 1: Chuẩn bị

### 1.1. Đảm bảo code đã push lên GitHub
```bash
# Kiểm tra
git status

# Nếu chưa push
git add .
git commit -m "Ready for Netlify deploy"
git push
```

### 1.2. Lấy URL Backend từ Render
- Vào [render.com](https://render.com)
- Chọn service backend của bạn
- Copy URL (ví dụ: `https://chatbot-backend-xxxx.onrender.com`)
- **Lưu lại URL này** - sẽ cần dùng sau

---

## 🌐 Bước 2: Đăng ký/Đăng nhập Netlify

1. **Vào [netlify.com](https://netlify.com)**
2. Click **"Sign up"** hoặc **"Log in"**
3. Chọn **"Sign up with GitHub"** (khuyến nghị)
4. Authorize Netlify truy cập GitHub của bạn

---

## 📦 Bước 3: Deploy từ GitHub

### 3.1. Tạo site mới

1. **Từ Netlify Dashboard:**
   - Click nút **"Add new site"** (góc trên bên phải)
   - Chọn **"Import an existing project"**

2. **Chọn GitHub:**
   - Click **"GitHub"** hoặc **"Deploy with GitHub"**
   - Nếu lần đầu, Netlify sẽ yêu cầu authorize
   - Click **"Authorize Netlify"**

3. **Chọn repository:**
   - Tìm và chọn repository của bạn
   - Click vào repository

### 3.2. Cấu hình Build Settings

Netlify sẽ tự động detect, nhưng cần kiểm tra:

**Basic build settings:**
- **Base directory**: Để trống (hoặc `.` nếu code ở root)
- **Build command**: `npm run build`
- **Publish directory**: `dist`

**Nếu không tự động detect:**
- Click **"Show advanced"**
- Điền thủ công:
  - Build command: `npm run build`
  - Publish directory: `dist`

### 3.3. Environment Variables (QUAN TRỌNG!)

1. **Click "Show advanced"** → **"New variable"**

2. **Thêm biến:**
   - **Key**: `VITE_API_URL`
   - **Value**: URL backend từ Render (ví dụ: `https://chatbot-backend-xxxx.onrender.com`)
   - Click **"Add variable"**

3. **Kiểm tra lại:**
   - Phải có ít nhất 1 variable: `VITE_API_URL`

### 3.4. Deploy!

1. **Click nút "Deploy site"** (màu xanh)
2. **Đợi build** (2-5 phút)
   - Sẽ thấy log build real-time
   - Nếu thành công → Status: "Published"

---

## ✅ Bước 4: Kiểm tra và cấu hình

### 4.1. Lấy URL Frontend

- Netlify sẽ tạo URL tự động: `https://random-name-123.netlify.app`
- URL này sẽ hiển thị sau khi deploy xong

### 4.2. Đổi tên site (tùy chọn)

1. Vào **"Site settings"** (từ dashboard)
2. Click **"Change site name"**
3. Nhập tên mới (ví dụ: `chatbot-app`)
4. URL mới sẽ là: `https://chatbot-app.netlify.app`

### 4.3. Kiểm tra hoạt động

1. **Mở URL frontend** trong browser
2. **Kiểm tra console** (F12):
   - Không có lỗi CORS
   - API calls đến đúng backend URL

---

## 🔄 Bước 5: Cập nhật nếu cần

### 5.1. Cập nhật Environment Variable

Nếu backend URL thay đổi:

1. Vào **"Site settings"** → **"Environment variables"**
2. Tìm `VITE_API_URL`
3. Click **"Edit"**
4. Sửa value → **"Save"**
5. Vào **"Deploys"** tab
6. Click **"Trigger deploy"** → **"Clear cache and deploy site"**

### 5.2. Auto-deploy

- **Mỗi khi push code lên GitHub:**
  - Netlify tự động detect
  - Tự động build và deploy
  - Không cần làm gì thêm!

---

## 🐛 Troubleshooting

### Lỗi: "Build failed"

**Nguyên nhân:**
- Build command sai
- Thiếu dependencies
- Lỗi trong code

**Giải pháp:**
1. Xem **"Deploy log"** để biết lỗi cụ thể
2. Test build local trước:
   ```bash
   npm run build
   ```
3. Sửa lỗi → Commit → Push → Auto-deploy lại

### Lỗi: "Cannot connect to backend"

**Nguyên nhân:**
- `VITE_API_URL` chưa set hoặc sai
- Backend chưa chạy

**Giải pháp:**
1. Kiểm tra Environment Variable `VITE_API_URL`
2. Kiểm tra backend đang chạy trên Render
3. Test backend: `https://your-backend.onrender.com/health`
4. Clear cache và deploy lại

### Lỗi: "CORS error"

**Nguyên nhân:**
- Backend chưa cho phép domain Netlify

**Giải pháp:**
- Backend đã có `CORS(app)` nên sẽ tự động cho phép
- Nếu vẫn lỗi, kiểm tra backend logs

### Site không load được

**Nguyên nhân:**
- Build failed
- Publish directory sai

**Giải pháp:**
1. Kiểm tra **"Deploy log"**
2. Kiểm tra **"Publish directory"** = `dist`
3. Rebuild: **"Deploys"** → **"Trigger deploy"**

---

## 📝 Checklist

- [ ] Code đã push lên GitHub
- [ ] Đã đăng ký/đăng nhập Netlify
- [ ] Đã tạo site từ GitHub repo
- [ ] Build settings đúng: `npm run build`, `dist`
- [ ] Đã thêm Environment Variable: `VITE_API_URL`
- [ ] Deploy thành công
- [ ] Có URL frontend
- [ ] Test thử app hoạt động
- [ ] Đổi tên site (tùy chọn)

---

## 🎯 Kết quả

Sau khi hoàn thành, bạn sẽ có:

- ✅ **Frontend URL**: `https://your-app.netlify.app`
- ✅ **Backend URL**: `https://your-backend.onrender.com`
- ✅ **Auto-deploy**: Tự động deploy khi push code
- ✅ **HTTPS**: Tự động có SSL certificate

---

## 💡 Tips

1. **Test local trước:**
   ```bash
   npm run build
   npm run preview
   ```

2. **Monitor deployments:**
   - Vào **"Deploys"** tab để xem lịch sử
   - Có thể rollback về version cũ nếu cần

3. **Custom domain:**
   - Có thể thêm domain riêng trong **"Domain settings"**
   - Netlify sẽ tự động setup SSL

4. **Analytics:**
   - Netlify có analytics miễn phí
   - Xem traffic, performance trong dashboard

---

## 📚 Tài liệu tham khảo

- [Netlify Docs](https://docs.netlify.com)
- [Vite Deployment Guide](https://vitejs.dev/guide/static-deploy.html#netlify)

