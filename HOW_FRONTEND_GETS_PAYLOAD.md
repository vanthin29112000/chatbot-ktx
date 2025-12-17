# 🔄 Cách Frontend Lấy Payload Từ Backend

## Luồng hoạt động:

```
Frontend (React)                    Backend (Flask/Playwright)
     |                                       |
     | 1. POST /api/capture-payload         |
     |------------------------------------->|
     |    { message: "hi" }                 |
     |                                       | 2. Khởi động Playwright
     |                                       |    - Mở browser
     |                                       |    - Truy cập trang chatbot
     |                                       |    - Nhắn "hi"
     |                                       |    - Bắt request → lấy payload
     |                                       |
     | 3. GET /api/capture-status           |
     |<--------------------------------------|
     |    { status: "capturing", ... }      |
     |                                       |
     | 4. Polling mỗi 500ms                  |
     |    GET /api/capture-status           |
     |<--------------------------------------|
     |    { status: "captured",             |
     |      payload: {...} }                |
     |                                       |
     | 5. Lưu payload vào state             |
     |    setPayloadTemplate(payload)       |
     |                                       |
```

## Code Frontend (đã có sẵn):

### 1. Gọi API capture:
```javascript
// File: src/App.jsx, dòng 302
const response = await fetch(`${BACKEND_API_URL}/api/capture-payload`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'hi' }),
})
```

### 2. Polling để lấy kết quả:
```javascript
// File: src/App.jsx, dòng 319-329
const checkStatus = async () => {
  const statusRes = await fetch(`${BACKEND_API_URL}/api/capture-status`)
  const status = await statusRes.json()
  
  if (status.status === 'captured' && status.payload) {
    // ✅ Lấy được payload!
    setPayloadTemplate(status.payload)
    // Payload đã được lưu vào state, có thể dùng ngay
  }
}
```

## Backend API Endpoints:

### 1. `/api/capture-payload` (POST)
- **Input**: `{ "message": "hi" }`
- **Output**: `{ "success": true, "message": "Đã bắt đầu capture..." }`
- **Chức năng**: Bắt đầu quá trình capture payload

### 2. `/api/capture-status` (GET)
- **Output**: 
  ```json
  {
    "status": "capturing" | "captured" | "error" | "idle",
    "payload": { ... } | null,
    "error": "..." | null,
    "message": "Đang khởi tạo trình duyệt..."
  }
  ```
- **Chức năng**: Kiểm tra trạng thái capture

### 3. `/api/get-payload` (GET)
- **Output**: `{ "success": true, "payload": { ... } }`
- **Chức năng**: Lấy payload đã capture (sau đó reset)

## Cách test:

### 1. Test Backend trực tiếp:
```bash
# Terminal 1: Chạy backend
python payload_capture_server.py

# Terminal 2: Test API
curl -X POST http://localhost:5000/api/capture-payload \
  -H "Content-Type: application/json" \
  -d '{"message": "hi"}'

# Kiểm tra status
curl http://localhost:5000/api/capture-status
```

### 2. Test Frontend:
```bash
# Terminal 1: Chạy backend
python payload_capture_server.py

# Terminal 2: Chạy frontend
npm run dev

# Mở browser: http://localhost:5173
# Frontend sẽ tự động gọi API và lấy payload
```

## Debug:

### Nếu không lấy được payload:

1. **Kiểm tra Backend có chạy không:**
   ```bash
   curl http://localhost:5000/health
   # Phải trả về: {"status": "ok"}
   ```

2. **Kiểm tra Backend có capture được không:**
   - Xem logs trong terminal chạy backend
   - Tìm dòng: `✅ Đã capture payload từ network request!`

3. **Kiểm tra Frontend có gọi API không:**
   - Mở DevTools (F12) → Network tab
   - Xem có request đến `/api/capture-payload` không
   - Xem có request đến `/api/capture-status` không

4. **Kiểm tra Environment Variable:**
   - Frontend cần biết `VITE_API_URL` (URL của backend)
   - Nếu không set, mặc định là `http://localhost:5000`

## Environment Variables:

### Frontend (.env hoặc Netlify):
```env
VITE_API_URL=https://your-backend.onrender.com
```

### Backend (Render):
```env
SHOW_BROWSER=false          # Ẩn browser (mặc định)
RECORD_VIDEO=false          # Không ghi video (mặc định)
PORT=5000                   # Port của server
```

## Kết quả:

Khi thành công, frontend sẽ:
1. ✅ Tự động lấy payload từ backend
2. ✅ Lưu vào `payloadTemplate` state
3. ✅ Dùng payload này để gửi tin nhắn đến chatbot
4. ✅ Hiển thị thông báo "✅ Đã tự động capture và lưu payload thành công!"

---

## Tóm tắt:

**Frontend không cần làm gì thêm!** Code đã có sẵn:
- ✅ Tự động gọi API khi vào trang
- ✅ Tự động polling để lấy payload
- ✅ Tự động lưu vào state
- ✅ Tự động dùng payload để chat

Chỉ cần đảm bảo:
1. Backend đang chạy
2. `VITE_API_URL` được set đúng
3. Backend có thể capture được payload (đã test với `simple_capture.py`)

