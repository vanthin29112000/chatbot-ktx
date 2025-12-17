# Hướng dẫn Tự động Capture Payload

## 🎯 Tổng quan

Có 2 cách để capture payload:

### Cách 1: Tự động hoàn toàn (Khuyến nghị) ⭐
Sử dụng Python Selenium để tự động hóa hoàn toàn quy trình.

### Cách 2: Thủ công
Copy script và chạy trên browser console (fallback).

---

## 🚀 Cách 1: Tự động với Python Selenium

### Bước 1: Cài đặt Python và dependencies

```bash
# Cài đặt Python packages
pip install -r requirements.txt

# Cài đặt ChromeDriver
# Option 1: Tự động (khuyến nghị)
pip install webdriver-manager

# Option 2: Thủ công
# Tải ChromeDriver từ: https://chromedriver.chromium.org/
# Đặt vào PATH hoặc cùng thư mục với script
```

### Bước 2: Khởi động Backend Server

```bash
python payload_capture_server.py
```

Server sẽ chạy tại `http://localhost:5000`

### Bước 3: Sử dụng trong React App

React app sẽ tự động gọi API backend để capture payload. Không cần thao tác gì thêm!

**Hoặc chạy script đơn giản:**
```bash
python capture_payload_simple.py "hi"
# Payload sẽ được lưu vào payload.json
```

---

## 📋 API Endpoints

### `POST /api/capture-payload`
Bắt đầu capture payload tự động.

**Request:**
```json
{
  "message": "hi"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Đã bắt đầu capture payload..."
}
```

### `GET /api/capture-status`
Kiểm tra trạng thái capture.

**Response:**
```json
{
  "status": "captured",  // idle, capturing, captured, error
  "payload": { ... },
  "error": null
}
```

### `GET /api/get-payload`
Lấy payload đã capture.

**Response:**
```json
{
  "success": true,
  "payload": { ... }
}
```

---

## 🔧 Cấu hình

### Thay đổi port server

Sửa trong `payload_capture_server.py`:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

### Thay đổi URL chatbot

Sửa trong cả 2 file Python:
```python
url = "https://trungtamquanlykytucxadhquocgiahcm.zapier.app/"
```

---

## 🐛 Troubleshooting

### Lỗi: `session not created: This version of ChromeDriver only supports Chrome version XXX`
**Nguyên nhân:** ChromeDriver version không khớp với Chrome browser version

**Giải pháp nhanh:**
```bash
# Chạy script tự động fix:
python update_chromedriver.py
```

**Giải pháp thủ công:**
```bash
# 1. Xóa cache và update webdriver-manager
rmdir /s "%USERPROFILE%\.wdm"
pip install --upgrade webdriver-manager selenium

# 2. Hoặc tải ChromeDriver thủ công:
# - Kiểm tra Chrome version: chrome://version
# - Tải ChromeDriver từ: https://googlechromelabs.github.io/chrome-for-testing/
# - Đặt vào PATH hoặc cùng thư mục với script
```

### Lỗi: `[WinError 193] %1 is not a valid Win32 application`
**Nguyên nhân:** ChromeDriver không tương thích (sai architecture hoặc version)

**Giải pháp:**
```bash
# 1. Chạy script kiểm tra
python fix_chromedriver.py

# 2. Chạy script update
python update_chromedriver.py
```

### Lỗi: ChromeDriver not found
```bash
pip install webdriver-manager
# Hoặc tải thủ công từ https://chromedriver.chromium.org/
```

### Lỗi: Cannot connect to backend
- Kiểm tra server đã chạy: `python payload_capture_server.py`
- Kiểm tra port 5000 không bị chặn
- React app sẽ tự động fallback sang phương pháp thủ công

### Lỗi: Cannot find textarea
- Có thể selector đã thay đổi
- Kiểm tra lại selector trong code
- Thử mở browser và inspect element

---

## 📝 Lưu ý

1. **ChromeDriver version**: Phải tương thích với Chrome version
2. **Network delay**: Có thể cần tăng timeout nếu mạng chậm
3. **Browser automation**: Browser sẽ tự động mở và đóng

---

## 🎉 Hoàn thành!

Sau khi capture thành công, payload sẽ tự động được lưu vào:
- `localStorage` trong React app
- File `payload.json` (nếu dùng script đơn giản)

