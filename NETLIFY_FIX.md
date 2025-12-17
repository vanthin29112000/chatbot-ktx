# 🔧 Fix Netlify Python Build Error

## Vấn đề:
Netlify tự động detect Python và cố cài `greenlet` (dependency của SQLAlchemy) khi build frontend.

## Giải pháp:

### Cách 1: Tắt Python trong Netlify UI (Khuyến nghị)

1. Vào **Netlify Dashboard** → **Site settings**
2. Vào **Build & deploy** → **Environment**
3. Thêm Environment Variable:
   - Key: `PYTHON_VERSION`
   - Value: (để trống hoặc xóa nếu có)
4. **Clear cache and deploy site**

### Cách 2: Đổi tên requirements.txt (Tạm thời)

Nếu cách 1 không work, có thể đổi tên `requirements.txt` thành `requirements.txt.backend`:

```bash
# Chỉ làm nếu cách 1 không work
git mv requirements.txt requirements.txt.backend
```

Sau đó cập nhật `Dockerfile`:
```dockerfile
COPY requirements.txt.backend requirements.txt
```

### Cách 3: Tạo file để force Node.js

Đã tạo `.nvmrc` để force Node.js version.

---

## Files đã tạo:

✅ `.netlifyignore` - Loại bỏ Python files khỏi Netlify build
✅ `.nvmrc` - Force Node.js version
✅ `netlify.toml` - Cấu hình tắt Python

---

## Bước tiếp theo:

1. **Trên Netlify UI:**
   - Vào **Site settings** → **Build & deploy** → **Environment**
   - Xóa hoặc để trống `PYTHON_VERSION` nếu có
   - **Clear cache and deploy site**

2. **Hoặc push code mới:**
   ```bash
   git add .netlifyignore .nvmrc netlify.toml
   git commit -m "Fix Netlify: Disable Python build"
   git push origin main
   ```

3. **Trigger rebuild trên Netlify:**
   - Vào **Deploys** tab
   - Click **"Trigger deploy"** → **"Clear cache and deploy site"**

---

## Nếu vẫn lỗi:

Có thể cần đổi tên `requirements.txt` tạm thời (Cách 2 ở trên).

