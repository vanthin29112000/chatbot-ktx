# Hướng dẫn Deploy lên GitHub và các dịch vụ

## 📋 Mục lục
1. [Chuẩn bị code](#chuẩn-bị-code)
2. [Tạo GitHub Repository](#tạo-github-repository)
3. [Push code lên GitHub](#push-code-lên-github)
4. [Deploy Frontend lên Netlify](#deploy-frontend-lên-netlify)
5. [Deploy Backend lên Render](#deploy-backend-lên-render)

---

## 🔧 Chuẩn bị code

### Bước 1: Kiểm tra .gitignore

Đảm bảo file `.gitignore` có các nội dung sau:

```
# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Environment variables
.env
.env.local
.env.production

# Build outputs
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*

# Chrome/Selenium
chromedriver
*.crx
```

### Bước 2: Kiểm tra các file cần thiết

Đảm bảo có các file sau:
- ✅ `package.json` (Frontend)
- ✅ `requirements.txt` (Backend)
- ✅ `Dockerfile` (cho Render)
- ✅ `render.yaml` (cho Render)
- ✅ `netlify.toml` (cho Netlify)
- ✅ `vite.config.js`
- ✅ `payload_capture_server.py`

---

## 🚀 Tạo GitHub Repository

### Cách 1: Tạo repo trên GitHub.com (Khuyến nghị)

1. **Đăng nhập GitHub:**
   - Vào [github.com](https://github.com)
   - Đăng nhập hoặc tạo tài khoản mới

2. **Tạo repository mới:**
   - Click nút **"+"** ở góc trên bên phải
   - Chọn **"New repository"**
   - Điền thông tin:
     - **Repository name**: `chatbot-app` (hoặc tên bạn muốn)
     - **Description**: "Chatbot với React và Flask"
     - **Visibility**: Chọn **Public** (để free deploy) hoặc **Private**
     - **Không** tích "Initialize with README" (vì đã có code)
   - Click **"Create repository"**

3. **Copy URL repository:**
   - Sẽ có URL dạng: `https://github.com/username/chatbot-app.git`
   - Lưu lại URL này

---

## 📤 Push code lên GitHub

### Cách 1: Dùng Git Command Line (Khuyến nghị)

#### Bước 1: Mở Terminal/Command Prompt

Trong thư mục project của bạn:
```bash
cd "C:\Users\pvthin\Desktop\project\test chat bot"
```

#### Bước 2: Khởi tạo Git (nếu chưa có)

```bash
# Kiểm tra xem đã có git chưa
git status

# Nếu chưa có, khởi tạo
git init
```

#### Bước 3: Thêm tất cả files

```bash
# Thêm tất cả files vào staging
git add .

# Kiểm tra files sẽ commit
git status
```

#### Bước 4: Commit lần đầu

```bash
git commit -m "Initial commit: Chatbot app with React and Flask"
```

#### Bước 5: Kết nối với GitHub

```bash
# Thay YOUR_USERNAME và YOUR_REPO bằng thông tin của bạn
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Kiểm tra remote đã thêm chưa
git remote -v
```

#### Bước 6: Push code lên GitHub

```bash
# Push code lên branch main
git branch -M main
git push -u origin main
```

**Nếu lần đầu push, GitHub sẽ yêu cầu đăng nhập:**
- Username: Tên GitHub của bạn
- Password: **Personal Access Token** (không phải password GitHub)

**Tạo Personal Access Token:**
1. Vào GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Chọn quyền: `repo` (full control)
4. Copy token và dùng làm password

---

### Cách 2: Dùng GitHub Desktop (Dễ hơn cho người mới)

1. **Download GitHub Desktop:**
   - Vào [desktop.github.com](https://desktop.github.com)
   - Download và cài đặt

2. **Đăng nhập:**
   - Mở GitHub Desktop
   - Đăng nhập với tài khoản GitHub

3. **Add repository:**
   - Click **"File"** → **"Add Local Repository"**
   - Chọn thư mục project: `C:\Users\pvthin\Desktop\project\test chat bot`
   - Click **"Add repository"**

4. **Commit và Push:**
   - Ở bên trái, nhập commit message: "Initial commit"
   - Click **"Commit to main"**
   - Click **"Publish repository"**
   - Chọn tên repo và click **"Publish repository"**

---

### Cách 3: Dùng VS Code (Nếu bạn dùng VS Code)

1. **Mở project trong VS Code:**
   ```bash
   code "C:\Users\pvthin\Desktop\project\test chat bot"
   ```

2. **Mở Source Control:**
   - Click icon Source Control ở sidebar (hoặc `Ctrl+Shift+G`)

3. **Initialize Repository:**
   - Nếu chưa có git, click "Initialize Repository"

4. **Stage và Commit:**
   - Click dấu "+" để stage all changes
   - Nhập commit message: "Initial commit"
   - Click "Commit"

5. **Push:**
   - Click "..." → "Push"
   - Chọn "Publish to GitHub"
   - Chọn tên repo và click "Publish"

---

## 🌐 Deploy Frontend lên Netlify

### Bước 1: Đăng ký Netlify

1. Vào [netlify.com](https://netlify.com)
2. Click **"Sign up"** → Chọn **"GitHub"**
3. Authorize Netlify truy cập GitHub

### Bước 2: Deploy từ GitHub

1. **Từ dashboard Netlify:**
   - Click **"Add new site"** → **"Import an existing project"**
   - Chọn **"GitHub"**
   - Chọn repository của bạn

2. **Cấu hình build:**
   - **Build command**: `npm run build`
   - **Publish directory**: `dist`
   - Click **"Show advanced"** → **"New variable"**
     - Key: `VITE_API_URL`
     - Value: `https://your-backend.onrender.com` (sẽ cập nhật sau khi deploy backend)

3. **Deploy:**
   - Click **"Deploy site"**
   - Đợi build xong (2-3 phút)

4. **Lấy URL:**
   - Netlify sẽ tạo URL dạng: `https://random-name-123.netlify.app`
   - Có thể đổi tên trong **"Site settings"** → **"Change site name"**

---

## 🖥️ Deploy Backend lên Render

### Bước 1: Đăng ký Render

1. Vào [render.com](https://render.com)
2. Click **"Get Started for Free"**
3. Chọn **"Sign up with GitHub"**
4. Authorize Render truy cập GitHub

### Bước 2: Deploy Web Service

1. **Từ dashboard Render:**
   - Click **"New +"** → **"Web Service"**
   - Chọn repository của bạn

2. **Cấu hình:**
   - **Name**: `chatbot-backend` (hoặc tên bạn muốn)
   - **Environment**: **Docker**
   - **Region**: Chọn gần bạn nhất (Singapore hoặc US)
   - **Branch**: `main`
   - **Root Directory**: Để trống (hoặc `.` nếu có subfolder)
   - **Dockerfile Path**: `./Dockerfile`
   - **Docker Build Context**: Để trống

3. **Environment Variables:**
   - Click **"Advanced"** → **"Add Environment Variable"**
   - Thêm:
     - `PORT` = `5000`
     - `FLASK_ENV` = `production`

4. **Plan:**
   - Chọn **"Free"**

5. **Deploy:**
   - Click **"Create Web Service"**
   - Đợi build (5-10 phút lần đầu, vì cần cài Chrome)

6. **Lấy URL:**
   - Render sẽ tạo URL dạng: `https://chatbot-backend.onrender.com`
   - Copy URL này

### Bước 3: Cập nhật Frontend

1. **Quay lại Netlify:**
   - Vào **"Site settings"** → **"Environment variables"**
   - Sửa `VITE_API_URL` = `https://your-backend.onrender.com`
   - Click **"Save"**
   - Vào **"Deploys"** → **"Trigger deploy"** → **"Clear cache and deploy site"**

---

## 🔄 Auto-deploy

Sau khi setup xong:

- **Mỗi khi push code lên GitHub:**
  - Netlify tự động build và deploy frontend
  - Render tự động build và deploy backend

- **Workflow:**
  ```
  Code thay đổi
    ↓
  git add .
  git commit -m "Update"
  git push
    ↓
  GitHub nhận code
    ↓
  Netlify auto-deploy frontend
  Render auto-deploy backend
  ```

---

## ✅ Checklist

- [ ] Code đã push lên GitHub
- [ ] Frontend đã deploy lên Netlify
- [ ] Backend đã deploy lên Render
- [ ] Environment variable `VITE_API_URL` đã set đúng
- [ ] Test thử app hoạt động
- [ ] Setup keep-alive để tránh spin down (tùy chọn)

---

## 🐛 Troubleshooting

### Lỗi: "Cannot push to GitHub"
- Kiểm tra đã đăng nhập GitHub chưa
- Kiểm tra Personal Access Token
- Thử: `git remote set-url origin https://YOUR_TOKEN@github.com/USERNAME/REPO.git`

### Lỗi: "Build failed on Netlify"
- Kiểm tra `package.json` có đúng không
- Kiểm tra build command: `npm run build`
- Xem logs trong Netlify dashboard

### Lỗi: "Docker build failed on Render"
- Kiểm tra `Dockerfile` có đúng không
- Kiểm tra `requirements.txt` có đầy đủ không
- Xem logs trong Render dashboard

### Backend không chạy được Selenium
- Kiểm tra Chrome đã cài trong Dockerfile chưa
- Kiểm tra logs trong Render
- Thử test local với Docker: `docker build -t chatbot . && docker run -p 5000:5000 chatbot`

---

## 📚 Tài liệu tham khảo

- [GitHub Docs](https://docs.github.com)
- [Netlify Docs](https://docs.netlify.com)
- [Render Docs](https://render.com/docs)
- [Docker Docs](https://docs.docker.com)

---

## 💡 Tips

1. **Luôn test local trước khi push:**
   ```bash
   # Test frontend
   npm run build
   npm run preview
   
   # Test backend
   python payload_capture_server.py
   ```

2. **Commit thường xuyên:**
   - Commit nhỏ, thường xuyên
   - Message rõ ràng: "Fix: Sửa lỗi loading", "Feat: Thêm popup đánh giá"

3. **Branch protection:**
   - Có thể tạo branch `develop` để test
   - Chỉ merge vào `main` khi đã test kỹ

4. **Monitor:**
   - Dùng [UptimeRobot](https://uptimerobot.com) để monitor backend
   - Ping `/keep-alive` mỗi 5 phút để tránh spin down

