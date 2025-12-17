"""
Script đơn giản để capture payload từ Zapier chatbot
Chỉ cần chạy script này, nó sẽ tự động:
1. Mở browser (có thể thấy được)
2. Truy cập trang chatbot
3. Nhắn tin "hi"
4. Bắt request và lấy payload
5. In ra payload
"""
from playwright.sync_api import sync_playwright
import json
import time

def capture_payload_simple():
    """Capture payload một cách đơn giản"""
    
    print("🚀 Bắt đầu capture payload...")
    print("=" * 60)
    
    with sync_playwright() as p:
        # Mở browser có thể thấy được (headless=False)
        print("🌐 Đang mở browser...")
        browser = p.chromium.launch(
            headless=False,  # Hiển thị browser để bạn có thể thấy
            slow_mo=500,  # Chậm lại 500ms mỗi action để dễ quan sát
        )
        
        # Tạo context và page
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()
        
        # Biến để lưu payload
        captured_payload = None
        
        # Hàm để bắt request
        def handle_request(request):
            if '/api/chat' in request.url and request.method == 'POST':
                try:
                    post_data = request.post_data
                    if post_data:
                        if isinstance(post_data, str):
                            payload = json.loads(post_data)
                        else:
                            payload = post_data
                        
                        nonlocal captured_payload
                        captured_payload = payload
                        print("\n" + "=" * 60)
                        print("✅ ĐÃ CAPTURE PAYLOAD THÀNH CÔNG!")
                        print("=" * 60)
                        print(json.dumps(payload, indent=2, ensure_ascii=False))
                        print("=" * 60)
                except Exception as e:
                    print(f"⚠️  Lỗi: {e}")
        
        # Lắng nghe requests
        page.on("request", handle_request)
        
        # Truy cập trang chatbot
        url = "https://trungtamquanlykytucxadhquocgiahcm.zapier.app/"
        print(f"📡 Đang truy cập: {url}")
        page.goto(url, wait_until="networkidle")
        
        print("⏳ Đang chờ trang load...")
        time.sleep(2)
        
        # Tìm textarea
        print("🔍 Đang tìm ô nhập tin nhắn...")
        textarea = None
        selectors = ['textarea', 'input[type="text"]']
        
        for selector in selectors:
            try:
                textarea = page.wait_for_selector(selector, timeout=5000)
                if textarea:
                    print(f"✅ Tìm thấy ô nhập với selector: {selector}")
                    break
            except:
                continue
        
        if not textarea:
            print("❌ Không tìm thấy ô nhập tin nhắn!")
            browser.close()
            return None
        
        # Nhập tin nhắn
        print("⌨️  Đang nhập tin nhắn 'hi'...")
        textarea.click()
        time.sleep(0.5)
        textarea.fill("hi")
        time.sleep(0.5)
        
        # Gửi tin nhắn (Enter)
        print("📤 Đang gửi tin nhắn...")
        textarea.press("Enter")
        
        # Chờ payload được capture (tối đa 10 giây)
        print("⏳ Đang chờ capture payload...")
        for i in range(20):  # 20 lần x 0.5s = 10 giây
            if captured_payload:
                break
            time.sleep(0.5)
            if i % 4 == 0:  # In mỗi 2 giây
                print(f"   Đang chờ... ({i * 0.5:.1f}s)")
        
        # Đợi thêm một chút để đảm bảo
        time.sleep(2)
        
        if captured_payload:
            print("\n✅ HOÀN THÀNH! Payload đã được capture ở trên.")
            print("\n💡 Bạn có thể:")
            print("   1. Copy payload ở trên")
            print("   2. Hoặc lưu vào file bằng cách chạy: python simple_capture.py > payload.json")
        else:
            print("\n❌ Không capture được payload sau 10 giây")
            print("💡 Hãy thử:")
            print("   1. Kiểm tra xem browser có mở không")
            print("   2. Xem có tin nhắn được gửi không")
            print("   3. Mở DevTools (F12) và xem Network tab")
        
        # Giữ browser mở thêm 5 giây để bạn có thể xem
        print("\n⏳ Browser sẽ đóng sau 5 giây...")
        time.sleep(5)
        
        browser.close()
        
        return captured_payload

if __name__ == "__main__":
    payload = capture_payload_simple()
    
    if payload:
        print("\n" + "=" * 60)
        print("📋 PAYLOAD CUỐI CÙNG:")
        print("=" * 60)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print("=" * 60)

