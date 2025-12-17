# 🚀 Quick Start - Deploy lên GitHub

## Các bước nhanh (5 phút)

### 1. Tạo GitHub Repository

```bash
# Mở terminal trong thư mục project
cd "C:\Users\pvthin\Desktop\project\test chat bot"

# Khởi tạo git (nếu chưa có)
git init

# Thêm tất cả files
git add .

# Commit
git commit -m "Initial commit"

# Tạo repo trên GitHub.com trước, sau đó:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### 2. Deploy Frontend (Netlify)

1. Vào [netlify.com](https://netlify.com) → Sign up với GitHub
2. "Add new site" → "Import from Git" → Chọn repo
3. Build settings:
   - Build command: `npm run build`
   - Publish directory: `dist`
4. Environment variables:
   - `VITE_API_URL` = `https://your-backend.onrender.com` (sẽ cập nhật sau)
5. Deploy!

### 3. Deploy Backend (Render)

1. Vào [render.com](https://render.com) → Sign up với GitHub
2. "New +" → "Web Service" → Chọn repo
3. Settings:
   - Environment: **Docker**
   - Dockerfile Path: `./Dockerfile`
   - Port: `5000`
4. Environment variables:
   - `PORT` = `5000`
   - `FLASK_ENV` = `production`
5. Plan: **Free**
6. Deploy!

### 4. Cập nhật Frontend

1. Quay lại Netlify
2. Site settings → Environment variables
3. Sửa `VITE_API_URL` = URL backend từ Render
4. Trigger deploy lại

## ✅ Done!

Bây giờ bạn có:
- Frontend: `https://your-app.netlify.app`
- Backend: `https://your-backend.onrender.com`

Xem file `GITHUB_DEPLOY.md` để biết chi tiết hơn!

