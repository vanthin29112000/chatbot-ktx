# 🔧 Fix lỗi 404 trên Netlify - Hướng dẫn cuối cùng

## ✅ Đã kiểm tra:

1. ✅ File `public/_redirects` đã có
2. ✅ File `_redirects` đã được copy vào `dist` sau khi build
3. ✅ File `netlify.toml` đã có redirect rules

## 🔄 Các bước fix:

### Bước 1: Commit và push code

```bash
git add netlify.toml public/_redirects
git commit -m "Fix: Add SPA redirect rules with force flag"
git push
```

### Bước 2: Rebuild trên Netlify với Clear Cache

1. **Vào Netlify Dashboard**
2. **Chọn site của bạn**
3. **Vào tab "Deploys"**
4. **Click "Trigger deploy"** → **"Clear cache and deploy site"**
5. **Đợi build xong** (2-3 phút)

### Bước 3: Kiểm tra Redirect Rules

1. **Vào "Site settings"** → **"Build & deploy"**
2. **Scroll xuống "Post processing"**
3. **Kiểm tra có redirect rule:**
   - `/*` → `/index.html` (200)

### Bước 4: Test lại

- Truy cập URL chính: `https://your-site.netlify.app`
- Thử refresh trang (F5)
- Thử truy cập trực tiếp: `https://your-site.netlify.app/index.html`

## 🐛 Nếu vẫn lỗi 404:

### Cách 1: Kiểm tra Build Logs

1. Vào **"Deploys"** → Click deploy mới nhất
2. Xem **"Publish log"**
3. Kiểm tra có file `_redirects` trong danh sách files không

### Cách 2: Kiểm tra File Structure

Sau khi build, `dist` folder phải có:
```
dist/
  ├── _redirects          ← Phải có file này
  ├── index.html
  └── assets/
      ├── index-xxxxx.js
      └── index-xxxxx.css
```

### Cách 3: Test local với Netlify CLI

```bash
# Cài Netlify CLI
npm install -g netlify-cli

# Test local
netlify dev
```

### Cách 4: Kiểm tra Netlify Settings

1. **Site settings** → **"Build & deploy"**
2. **Build settings:**
   - Build command: `npm run build`
   - Publish directory: `dist`
3. **Post processing:**
   - Phải có redirect rule

## 💡 Alternative: Dùng Netlify UI

Nếu file `_redirects` không hoạt động:

1. Vào **"Site settings"** → **"Build & deploy"**
2. Scroll xuống **"Post processing"**
3. Click **"Add redirect rule"**
4. Thêm:
   - **From**: `/*`
   - **To**: `/index.html`
   - **Status**: `200`
5. **Save**

## ✅ Checklist

- [ ] File `public/_redirects` đã có
- [ ] File `_redirects` có trong `dist` sau khi build
- [ ] File `netlify.toml` đã có redirect rules với `force = true`
- [ ] Code đã commit và push
- [ ] Đã rebuild trên Netlify với clear cache
- [ ] Test lại trang web

## 📝 Lưu ý

- **File `_redirects`** trong `public` folder sẽ được Vite tự động copy vào `dist`
- **Netlify sẽ đọc file `_redirects`** trong `dist` folder
- **Nếu vẫn không được**, có thể thêm redirect rule trực tiếp trong Netlify UI

