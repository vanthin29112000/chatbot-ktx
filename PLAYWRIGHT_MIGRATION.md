# 🎭 Chuyển đổi từ Selenium sang Playwright

## 📊 So sánh Selenium vs Playwright

### ✅ Ưu điểm của Playwright:

1. **Nhẹ hơn và nhanh hơn**
   - Không cần cài Chrome/Chromium riêng
   - Tự động download browser khi cần
   - Performance tốt hơn Selenium

2. **Dễ cài đặt hơn**
   - Không cần ChromeDriver
   - Không cần webdriver-manager
   - Chỉ cần `pip install playwright` và `playwright install chromium`

3. **API đơn giản hơn**
   - Code ngắn gọn hơn (~200 dòng vs ~600 dòng)
   - Dễ đọc và maintain hơn
   - Ít lỗi hơn

4. **Capture network requests dễ hơn**
   - Built-in event listener cho network requests
   - Không cần CDP (Chrome DevTools Protocol) phức tạp

5. **Tốt hơn cho headless browser**
   - Được thiết kế cho headless từ đầu
   - Ít vấn đề với headless mode

### ⚠️ Nhược điểm:

1. **File size lớn hơn một chút**
   - Playwright download browser (~150MB)
   - Nhưng chỉ download một lần

2. **Mới hơn Selenium**
   - Ít tài liệu hơn (nhưng đủ dùng)
   - Cộng đồng nhỏ hơn (nhưng đang phát triển nhanh)

---

## 🚀 Cách chuyển đổi

### Option 1: Thay thế hoàn toàn (Khuyến nghị)

1. **Backup file cũ:**
   ```bash
   cp payload_capture_server.py payload_capture_server_selenium.py.backup
   ```

2. **Thay thế file:**
   ```bash
   cp payload_capture_server_playwright.py payload_capture_server.py
   ```

3. **Cập nhật requirements.txt:**
   ```bash
   cp requirements_playwright.txt requirements.txt
   ```

4. **Cập nhật Dockerfile:**
   ```bash
   cp Dockerfile.playwright Dockerfile
   ```

5. **Test local:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   python payload_capture_server.py
   ```

6. **Deploy lên Render:**
   - Push code lên GitHub
   - Render sẽ tự động rebuild với Dockerfile mới

### Option 2: Giữ cả hai (để test)

1. **Giữ cả hai file:**
   - `payload_capture_server.py` (Selenium - hiện tại)
   - `payload_capture_server_playwright.py` (Playwright - mới)

2. **Test Playwright version:**
   ```bash
   pip install -r requirements_playwright.txt
   playwright install chromium
   python payload_capture_server_playwright.py
   ```

3. **Khi đã test xong, chuyển sang Option 1**

---

## 📝 Thay đổi chính trong code

### Selenium (cũ):
```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
driver.get(url)
textarea = driver.find_element(By.CSS_SELECTOR, "textarea")
textarea.send_keys("hi")
textarea.send_keys(Keys.RETURN)

# Capture network requests (phức tạp)
driver.execute_cdp_cmd('Network.enable', {})
logs = driver.get_log('performance')
# Parse logs để tìm payload...
```

### Playwright (mới):
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Capture network requests (đơn giản)
    def handle_request(request):
        if '/api/chat' in request.url:
            payload = json.loads(request.post_data)
            # Done!
    
    page.on("request", handle_request)
    page.goto(url)
    page.fill("textarea", "hi")
    page.press("textarea", "Enter")
```

---

## 🐳 Dockerfile so sánh

### Selenium Dockerfile:
- Cần cài Chromium + chromium-driver
- Cần tạo symlink
- ~50 dòng code
- Build time: ~5-10 phút

### Playwright Dockerfile:
- Chỉ cần dependencies cơ bản
- Playwright tự download browser
- ~30 dòng code
- Build time: ~3-5 phút (nhanh hơn!)

---

## 💡 Lợi ích khi deploy trên Render

1. **Build nhanh hơn**
   - Không cần cài Chrome/Chromium trong Dockerfile
   - Playwright tự download browser khi chạy

2. **Ít lỗi hơn**
   - Không cần lo về ChromeDriver version mismatch
   - Không cần webdriver-manager

3. **Code sạch hơn**
   - Dễ maintain
   - Dễ debug

---

## 🧪 Test

Sau khi chuyển đổi, test các chức năng:

1. ✅ Capture payload tự động
2. ✅ Proxy API chat (tránh CORS)
3. ✅ Health check endpoint
4. ✅ Keep-alive endpoint

---

## 📚 Tài liệu tham khảo

- [Playwright Python Docs](https://playwright.dev/python/)
- [Playwright Network Events](https://playwright.dev/python/docs/network)
- [Playwright Docker](https://playwright.dev/python/docs/docker)

---

## ❓ FAQ

**Q: Có cần thay đổi frontend không?**  
A: Không, frontend không cần thay đổi gì. API endpoints giữ nguyên.

**Q: Playwright có free không?**  
A: Có, Playwright hoàn toàn miễn phí và open source.

**Q: Có thể dùng cả Selenium và Playwright không?**  
A: Có thể, nhưng không cần thiết. Chọn một cái thôi.

**Q: Playwright có hỗ trợ Firefox/Safari không?**  
A: Có, nhưng cho use case này, Chromium là đủ.

---

## ✅ Kết luận

**Khuyến nghị: Chuyển sang Playwright**

- ✅ Nhẹ hơn
- ✅ Dễ cài hơn
- ✅ Code sạch hơn
- ✅ Ít lỗi hơn
- ✅ Build nhanh hơn

Chỉ cần thay file và deploy lại là xong! 🎉

