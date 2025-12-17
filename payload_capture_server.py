"""
Payload Capture Server - Tự động capture payload từ Zapier chatbot
Sử dụng Playwright thay vì Selenium (nhẹ hơn, dễ cài hơn)
"""
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import json
import time
import threading
import os
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

app = Flask(__name__)
CORS(app)

# Global variables để lưu payload
captured_payload = None
capture_status = {
    "status": "idle",  # idle, capturing, captured, error
    "payload": None,
    "error": None
}

def capture_payload_playwright(initial_message="hi"):
    """Sử dụng Playwright để tự động capture payload"""
    global captured_payload, capture_status, is_capturing
    
    capture_status["status"] = "capturing"
    capture_status["error"] = None
    
    try:
        print("🚀 Khởi tạo Playwright browser...")
        capture_status["message"] = "Đang khởi tạo trình duyệt..."
        
        with sync_playwright() as p:
            # Khởi tạo browser với headless mode
            print("🌐 Đang khởi động browser...")
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                ]
            )
            
            # Tạo context với viewport size
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            page = context.new_page()
            
            # Biến để lưu captured payload
            captured_payload_from_network = [None]
            
            # URL mục tiêu cần capture
            target_url = "https://trungtamquanlykytucxadhquocgiahcm.zapier.app/api/chat"
            
            # Lắng nghe network requests - dùng route để intercept và lấy post data
            def handle_route(route):
                request = route.request
                if '/api/chat' in request.url and request.method == 'POST':
                    try:
                        # Lấy post_data từ request
                        post_data = request.post_data
                        
                        if post_data:
                            # Parse JSON payload
                            if isinstance(post_data, str):
                                payload = json.loads(post_data)
                            elif isinstance(post_data, dict):
                                payload = post_data
                            else:
                                # Thử decode nếu là bytes
                                try:
                                    post_data_str = post_data.decode('utf-8') if isinstance(post_data, bytes) else str(post_data)
                                    payload = json.loads(post_data_str)
                                except:
                                    payload = post_data
                            
                            captured_payload_from_network[0] = payload
                            print(f"✅ Đã capture payload từ network request!")
                            print(f"📋 Request URL: {request.url}")
                            print(f"📋 Request Method: {request.method}")
                            print(f"📦 Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
                        else:
                            print(f"⚠️  POST request đến {request.url} nhưng không có post_data")
                            print(f"⚠️  Request headers: {request.headers}")
                    except Exception as e:
                        print(f"⚠️  Lỗi khi parse payload: {e}")
                        print(f"⚠️  Request details: URL={request.url}, Method={request.method}")
                        import traceback
                        traceback.print_exc()
                
                # Tiếp tục request bình thường
                route.continue_()
            
            # Intercept tất cả requests - chỉ intercept requests đến target URL
            page.route("**/api/chat", handle_route)
            
            url = "https://trungtamquanlykytucxadhquocgiahcm.zapier.app/"
            print(f"📡 Đang mở trang web: {url}")
            capture_status["message"] = "Đang truy cập trang web..."
            page.goto(url, wait_until="networkidle", timeout=30000)
            
            print("⏳ Đang chờ trang web load...")
            capture_status["message"] = "Đang chờ trang web load..."
            time.sleep(2)  # Đợi thêm một chút để trang load hoàn toàn
            
            capture_status["message"] = "Đang tìm input field..."
            
            # Tìm textarea để nhập message
            textarea_selectors = [
                'textarea[placeholder*="Nhập"]',
                'textarea[placeholder*="câu hỏi"]',
                'textarea[data-testid*="prompt"]',
                'textarea',
                'input[type="text"]'
            ]
            
            textarea = None
            for selector in textarea_selectors:
                try:
                    textarea = page.wait_for_selector(selector, timeout=5000, state="visible")
                    if textarea:
                        print(f"✅ Tìm thấy input với selector: {selector}")
                        break
                except PlaywrightTimeoutError:
                    continue
            
            if not textarea:
                raise Exception("Không tìm thấy textarea để nhập message")
            
            # Scroll element vào view
            textarea.scroll_into_view_if_needed()
            time.sleep(0.5)
            
            # Nhập message
            print(f"⌨️  Đang nhập message: '{initial_message}'")
            capture_status["message"] = "Đang nhập message..."
            
            # Click và focus vào textarea
            textarea.click()
            time.sleep(0.2)
            textarea.fill(initial_message)
            time.sleep(0.3)
            
            # Verify value đã được set
            actual_value = textarea.input_value()
            print(f"✅ Verified textarea value: '{actual_value}'")
            
            # Submit form - Gửi Enter key
            print("⌨️  Đang gửi Enter key để submit form...")
            capture_status["message"] = "Đang gửi message..."
            
            # Clear captured payload trước khi submit
            captured_payload_from_network[0] = None
            
            # Gửi Enter key
            textarea.press("Enter")
            time.sleep(0.5)
            
            # Nếu không có request, thử gửi Enter lần nữa
            if not captured_payload_from_network[0]:
                textarea.press("Enter")
                time.sleep(0.5)
            
            # Nếu vẫn không có, thử tìm và click submit button
            if not captured_payload_from_network[0]:
                print("🔍 Thử tìm và click submit button...")
                submit_selectors = [
                    'button[type="submit"]',
                    'button[aria-label*="Send"]',
                    'button[data-testid*="send"]',
                ]
                
                for selector in submit_selectors:
                    try:
                        submit_button = page.query_selector(selector)
                        if submit_button:
                            submit_button.click()
                            print(f"✅ Đã click submit button với selector: {selector}")
                            time.sleep(0.5)
                            break
                    except:
                        continue
            
            print(f"📤 Đã gửi message, đang chờ capture payload từ network request...")
            capture_status["message"] = "Đang chờ capture payload từ network..."
            
            # Chờ payload được capture (tối đa 20 giây)
            max_wait = 20
            check_interval = 0.3
            waited = 0
            
            while waited < max_wait:
                if captured_payload_from_network[0]:
                    payload = captured_payload_from_network[0]
                    captured_payload = payload
                    capture_status["status"] = "captured"
                    capture_status["payload"] = payload
                    capture_status["message"] = "Hoàn thành!"
                    # Reset flag ngay khi capture thành công
                    with capture_lock:
                        is_capturing = False
                    print(f"✅ Đã capture payload thành công!")
                    return payload
                
                time.sleep(check_interval)
                waited += check_interval
            
            # Nếu không capture được sau khi chờ
            raise Exception(f"Không tìm thấy network request POST đến {target_url} sau {max_wait} giây")
            
    except Exception as e:
        error_msg = f"Lỗi Playwright: {str(e)}"
        print(f"❌ {error_msg}")
        capture_status["status"] = "error"
        capture_status["error"] = error_msg
        # Reset flag ngay khi có lỗi
        with capture_lock:
            is_capturing = False
        return None

# Biến để track xem đang có capture nào đang chạy không
is_capturing = False
capture_lock = threading.Lock()

@app.route('/api/capture-payload', methods=['POST'])
def capture_payload():
    """API endpoint để bắt đầu capture payload"""
    global capture_status, is_capturing
    
    # Kiểm tra xem đã có capture đang chạy chưa
    with capture_lock:
        if is_capturing:
            return jsonify({
                "success": False,
                "message": "Đã có một quá trình capture đang chạy. Vui lòng đợi..."
            }), 400
        
        is_capturing = True
    
    try:
        data = request.json or {}
        initial_message = data.get('message', 'hi')
        
        # Chạy Playwright trong thread riêng để không block
        thread = threading.Thread(target=capture_payload_playwright, args=(initial_message,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "message": "Đã bắt đầu capture payload, vui lòng đợi..."
        })
    except Exception as e:
        with capture_lock:
            is_capturing = False
        return jsonify({
            "success": False,
            "message": f"Lỗi khi bắt đầu capture: {str(e)}"
        }), 500

@app.route('/api/capture-status', methods=['GET'])
def get_capture_status():
    """API endpoint để kiểm tra trạng thái capture"""
    global capture_status, is_capturing
    
    # Auto-reset flag nếu status đã hoàn thành (captured hoặc error) nhưng flag vẫn True
    if capture_status.get("status") in ["captured", "error"] and is_capturing:
        with capture_lock:
            is_capturing = False
            print("🔄 Auto-reset is_capturing flag vì status đã hoàn thành")
    
    return jsonify(capture_status)

@app.route('/api/get-payload', methods=['GET'])
def get_payload():
    """API endpoint để lấy payload đã capture"""
    global captured_payload, capture_status
    
    if captured_payload:
        # Reset sau khi lấy
        payload = captured_payload
        captured_payload = None
        capture_status = {
            "status": "idle",
            "payload": None,
            "error": None
        }
        return jsonify({
            "success": True,
            "payload": payload
        })
    else:
        return jsonify({
            "success": False,
            "message": "Chưa có payload được capture"
        }), 404

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def proxy_chat():
    """Proxy endpoint để forward requests đến Zapier chatbot (tránh CORS)"""
    # Handle preflight CORS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        # Lấy payload từ request
        payload = request.get_json()
        if not payload:
            return jsonify({"error": "No payload provided"}), 400
        
        # URL của Zapier chatbot
        chatbot_url = "https://trungtamquanlykytucxadhquocgiahcm.zapier.app/api/chat"
        
        print(f"📤 Forwarding request to Zapier chatbot: {chatbot_url}")
        print(f"📦 Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        # Forward request đến Zapier với streaming
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
        }
        
        # Gửi request với stream=True để nhận streaming response
        response = requests.post(
            chatbot_url,
            json=payload,
            headers=headers,
            stream=True,
            timeout=60
        )
        
        # Kiểm tra status code
        if response.status_code != 200:
            error_text = response.text
            print(f"❌ Error from Zapier: {response.status_code} - {error_text}")
            return jsonify({
                "error": f"Chatbot API error: {response.status_code}",
                "message": error_text
            }), response.status_code
        
        # Stream response về client
        def generate():
            try:
                # Stream từng chunk từ Zapier response
                for chunk in response.iter_content(chunk_size=8192, decode_unicode=False):
                    if chunk:
                        # Decode bytes to string nếu cần
                        try:
                            if isinstance(chunk, bytes):
                                chunk = chunk.decode('utf-8', errors='replace')
                            yield chunk
                        except Exception as decode_error:
                            print(f"⚠️  Error decoding chunk: {decode_error}")
                            # Vẫn yield chunk gốc nếu decode fail
                            if isinstance(chunk, bytes):
                                yield chunk.decode('utf-8', errors='ignore')
                            else:
                                yield str(chunk)
            except Exception as e:
                print(f"❌ Error streaming response: {e}")
                error_data = json.dumps({'error': str(e)}, ensure_ascii=False)
                yield f"data: {error_data}\n\n"
        
        # Trả về streaming response với CORS headers
        flask_response = Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            }
        )
        
        return flask_response
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Lỗi kết nối đến chatbot: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({
            "error": "Network error",
            "message": error_msg
        }), 500
    except Exception as e:
        error_msg = f"Lỗi không xác định: {str(e)}"
        print(f"❌ {error_msg}")
        return jsonify({
            "error": "Internal error",
            "message": error_msg
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

@app.route('/keep-alive', methods=['GET'])
def keep_alive():
    """Keep-alive endpoint để tránh spin down trên Render"""
    return jsonify({"status": "alive", "message": "Server is running"})

@app.route('/api/reset-capture', methods=['POST'])
def reset_capture():
    """API endpoint để reset capture flag (cho phép capture mới)"""
    global is_capturing, capture_status
    with capture_lock:
        is_capturing = False
        # Reset capture status về idle
        capture_status = {
            "status": "idle",
            "payload": None,
            "error": None
        }
        print("🔄 Capture flag đã được reset thủ công")
    return jsonify({
        "success": True,
        "message": "Capture flag đã được reset"
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print("=" * 60)
    print("🚀 Payload Capture Server (Playwright) đang khởi động...")
    print("=" * 60)
    print("\n📝 HƯỚNG DẪN:")
    print("1. Playwright sẽ tự động download browser khi chạy lần đầu")
    print(f"2. Server sẽ chạy tại: http://0.0.0.0:{port}")
    print("3. React app sẽ gọi API này để capture payload tự động")
    print("\n" + "=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
