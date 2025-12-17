# 🎯 Hướng dẫn Capture Payload Đơn Giản

## Cách 1: Dùng Script Python (Đơn giản nhất)

### Bước 1: Cài đặt Playwright
```bash
pip install playwright
playwright install chromium
```

### Bước 2: Chạy script
```bash
python simple_capture.py
```

Script sẽ:
- ✅ Tự động mở browser (bạn có thể thấy)
- ✅ Truy cập trang chatbot
- ✅ Tự động nhắn "hi"
- ✅ Bắt request và in ra payload
- ✅ Giữ browser mở 5 giây để bạn xem

### Kết quả:
Payload sẽ được in ra console. Bạn có thể copy và dùng.

---

## Cách 2: Dùng Browser Extension (Không cần code)

### Chrome/Edge:
1. Cài extension **"Request Interceptor"** hoặc **"ModHeader"**
2. Mở trang chatbot
3. Bật extension
4. Gửi tin nhắn
5. Xem request trong extension

### Firefox:
1. Cài extension **"HTTP Header Live"**
2. Tương tự như trên

---

## Cách 3: Dùng Browser DevTools (Cách thủ công)

### Bước 1: Mở trang chatbot
```
https://trungtamquanlykytucxadhquocgiahcm.zapier.app/
```

### Bước 2: Mở DevTools
- Nhấn `F12` hoặc `Ctrl+Shift+I` (Windows/Linux)
- Hoặc `Cmd+Option+I` (Mac)

### Bước 3: Vào tab Network
- Click tab **"Network"**
- Đảm bảo có checkbox **"Preserve log"** được bật

### Bước 4: Gửi tin nhắn
- Nhập "hi" vào ô chat
- Nhấn Enter hoặc click nút gửi

### Bước 5: Tìm request
- Trong danh sách requests, tìm request đến `/api/chat`
- Click vào request đó
- Vào tab **"Payload"** hoặc **"Request"**
- Copy JSON payload

---

## Cách 4: Dùng Proxy Tool (Nâng cao)

### mitmproxy:
```bash
# Cài đặt
pip install mitmproxy

# Chạy proxy
mitmproxy

# Cấu hình browser để dùng proxy
# Sau đó truy cập trang và gửi tin nhắn
# mitmproxy sẽ hiển thị tất cả requests
```

---

## So sánh các cách:

| Cách | Độ khó | Tự động | Cần code |
|------|--------|---------|----------|
| Script Python | ⭐ Dễ | ✅ Có | ✅ Có |
| Browser Extension | ⭐⭐ Trung bình | ❌ Không | ❌ Không |
| DevTools | ⭐ Dễ | ❌ Không | ❌ Không |
| Proxy Tool | ⭐⭐⭐ Khó | ❌ Không | ❌ Không |

---

## Khuyến nghị:

**Cho người mới:** Dùng **DevTools** (Cách 3) - đơn giản nhất, không cần cài gì

**Cho developer:** Dùng **Script Python** (Cách 1) - tự động, nhanh

**Cho test nhanh:** Dùng **Browser Extension** (Cách 2) - dễ dùng

---

## Troubleshooting:

### Script không chạy?
```bash
# Kiểm tra Playwright đã cài chưa
playwright --version

# Nếu chưa, cài lại
pip install playwright
playwright install chromium
```

### Không capture được payload?
1. Kiểm tra browser có mở không
2. Xem có tin nhắn được gửi không
3. Mở DevTools (F12) → Network tab → Xem có request `/api/chat` không

### Browser không hiển thị?
- Trên server (Render): Browser sẽ tự động chạy headless (ẩn)
- Trên local: Đảm bảo có display (Windows/Mac/Linux desktop)

---

## Lưu payload vào file:

```bash
# Lưu vào file JSON
python simple_capture.py > payload.json

# Hoặc chỉ lấy payload (bỏ qua các log)
python simple_capture.py 2>/dev/null | grep -A 1000 "PAYLOAD CUỐI CÙNG" > payload.json
```

