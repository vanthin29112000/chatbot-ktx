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
        print("🚀 Khởi tạo Playwright browser...", flush=True)
        capture_status["message"] = "Đang khởi tạo trình duyệt..."
        
        # Browser và dependencies đã được cài trong Dockerfile
        # Không cần kiểm tra lại để tối ưu thời gian
        
        with sync_playwright() as p:
            # Luôn chạy headless=True (ẩn browser) để tối ưu performance và tránh lỗi trên Render
            # Browser sẽ chạy ẩn, không cần display
            print(f"🌐 Đang khởi động browser (headless mode)...", flush=True)
            try:
                browser = p.chromium.launch(
                    headless=True,  # Luôn ẩn browser để tối ưu
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-gpu',  # Tắt GPU để tránh lỗi
                        '--disable-software-rasterizer',  # Tối ưu
                        '--disable-extensions',  # Tắt extensions không cần thiết
                    ],
                )
            except Exception as launch_err:
                error_str = str(launch_err).lower()
                if "missing dependencies" in error_str or "host system is missing" in error_str:
                    error_msg = (
                        "❌ Thiếu system dependencies để chạy browser.\n"
                        "💡 Vui lòng rebuild Docker image với Dockerfile đã được cập nhật để cài dependencies."
                    )
                    print(error_msg, flush=True)
                    raise Exception("Missing system dependencies. Please rebuild Docker image.")
                else:
                    raise
            
            # Tạo context với viewport size
            # Có thể record video nếu muốn (để debug)
            record_video = os.environ.get('RECORD_VIDEO', 'false').lower() == 'true'
            context_options = {
                'viewport': {'width': 1920, 'height': 1080},
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Thêm video recording nếu được bật
            if record_video:
                context_options['record_video_dir'] = '/tmp/playwright_videos'
                context_options['record_video_size'] = {'width': 1920, 'height': 1080}
                print("📹 Video recording đã được bật", flush=True)
            
            context = browser.new_context(**context_options)
            
            page = context.new_page()
            
            # Biến để lưu captured payload
            captured_payload_from_network = [None]
            
            # URL mục tiêu cần capture
            target_url = "https://trungtamquanlykytucxadhquocgiahcm.zapier.app/api/chat"
            
            # Lắng nghe network requests - dùng event listener (đơn giản hơn route)
            request_count = [0]  # Đếm số requests để debug
            
            def handle_request(request):
                request_count[0] += 1
                # Log tất cả requests đến /api/chat để debug
                if '/api/chat' in request.url:
                    print(f"🔍 [Request #{request_count[0]}] {request.method} {request.url}", flush=True)
                    print(f"   Headers: {dict(request.headers)}", flush=True)
                
                if '/api/chat' in request.url and request.method == 'POST':
                    try:
                        print(f"📥 Đang xử lý POST request đến {request.url}", flush=True)
                        # Lấy post_data từ request
                        post_data = request.post_data
                        print(f"   post_data type: {type(post_data)}", flush=True)
                        print(f"   post_data value: {post_data}", flush=True)
                        
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
                                except Exception as decode_err:
                                    print(f"   ⚠️  Lỗi decode: {decode_err}", flush=True)
                                    payload = post_data
                            
                            captured_payload_from_network[0] = payload
                            print(f"✅ Đã capture payload từ network request!", flush=True)
                            print(f"📋 Request URL: {request.url}", flush=True)
                            print(f"📋 Request Method: {request.method}", flush=True)
                            print(f"📦 Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}", flush=True)
                        else:
                            print(f"⚠️  POST request đến {request.url} nhưng không có post_data", flush=True)
                            print(f"   Request headers: {dict(request.headers)}", flush=True)
                    except Exception as e:
                        print(f"⚠️  Lỗi khi parse payload: {e}", flush=True)
                        import traceback
                        traceback.print_exc()
                        import sys
                        sys.stdout.flush()
            
            # Lắng nghe tất cả requests
            page.on("request", handle_request)
            print(f"👂 Đã đăng ký request listener", flush=True)
            
            url = "https://trungtamquanlykytucxadhquocgiahcm.zapier.app/"
            print(f"📡 Đang mở trang web: {url}", flush=True)
            capture_status["message"] = "Đang truy cập trang web..."
            
            # Thử load với nhiều strategies để tránh timeout
            # Strategy 1: Thử domcontentloaded (nhanh nhất, chỉ cần DOM)
            try:
                print(f"   Thử với domcontentloaded...", flush=True)
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                print(f"✅ Đã load trang web (domcontentloaded)", flush=True)
            except Exception as goto_err:
                # Strategy 2: Nếu domcontentloaded fail, thử commit (nhanh nhất nhưng không đợi DOM)
                print(f"⚠️  domcontentloaded failed, thử commit: {goto_err}", flush=True)
                try:
                    page.goto(url, wait_until="commit", timeout=20000)
                    print(f"✅ Đã commit navigation (commit)", flush=True)
                    # Đợi một chút sau commit để DOM có thời gian render
                    time.sleep(2)
                except Exception as commit_err:
                    # Strategy 3: Cuối cùng thử load (đợi load event)
                    print(f"⚠️  commit failed, thử load: {commit_err}", flush=True)
                    page.goto(url, wait_until="load", timeout=25000)
                    print(f"✅ Đã load trang web (load event)", flush=True)
            
            # Đợi element xuất hiện với timeout dài hơn vì có thể cần JS render
            capture_status["message"] = "Đang tìm input field..."
            print("⏳ Đang tìm input field...", flush=True)
            
            # Tìm textarea để nhập message - thêm nhiều selectors và timeout dài hơn
            textarea_selectors = [
                'textarea[placeholder*="Nhập"]',
                'textarea[placeholder*="câu hỏi"]',
                'textarea[placeholder*="message"]',
                'textarea[placeholder*="Message"]',
                'textarea[data-testid*="prompt"]',
                'textarea[data-testid*="input"]',
                'textarea[aria-label*="message"]',
                'textarea',
                'input[type="text"]',
                'input[placeholder*="Nhập"]',
                'input[placeholder*="message"]'
            ]
            
            textarea = None
            # Đợi element với timeout 10 giây (đủ thời gian cho JS render)
            # Thử từng selector với timeout ngắn hơn
            for selector in textarea_selectors:
                try:
                    print(f"   🔍 Đang thử selector: {selector}", flush=True)
                    textarea = page.wait_for_selector(selector, timeout=5000, state="visible")
                    if textarea:
                        print(f"✅ Tìm thấy input với selector: {selector}", flush=True)
                        break
                except PlaywrightTimeoutError:
                    print(f"   ⏭️  Selector '{selector}' không tìm thấy trong 5s, thử selector tiếp theo...", flush=True)
                    continue
                except Exception as e:
                    print(f"   ⚠️  Lỗi khi thử selector '{selector}': {e}", flush=True)
                    continue
            
            # Nếu vẫn không tìm thấy, thử query_selector_all để xem có element nào không
            if not textarea:
                print("⚠️  Không tìm thấy với wait_for_selector, thử query_selector_all...", flush=True)
                all_textareas = page.query_selector_all('textarea, input[type="text"]')
                print(f"   Tìm thấy {len(all_textareas)} textarea/input elements", flush=True)
                if all_textareas:
                    # Lấy element đầu tiên
                    textarea = all_textareas[0]
                    print(f"✅ Sử dụng element đầu tiên từ query_selector_all", flush=True)
            
            if not textarea:
                print("❌ Không tìm thấy textarea với bất kỳ selector nào", flush=True)
                raise Exception("Không tìm thấy textarea để nhập message")
            
            # Scroll element vào view - không cần sleep sau đó
            textarea.scroll_into_view_if_needed()
            
            # Nhập message
            print(f"⌨️  Đang nhập message: '{initial_message}'", flush=True)
            capture_status["message"] = "Đang nhập message..."
            
            # Click và fill vào textarea - tối ưu, không cần sleep nhiều
            textarea.click()
            # Không cần sleep, fill sẽ tự động đợi element ready
            textarea.fill(initial_message)
            
            # Verify value đã được set (nhanh)
            actual_value = textarea.input_value()
            print(f"✅ Verified textarea value: '{actual_value}'", flush=True)
            
            # Submit form - Gửi Enter key
            print("⌨️  Đang gửi Enter key để submit form...", flush=True)
            capture_status["message"] = "Đang gửi message..."
            
            # Clear captured payload trước khi submit
            captured_payload_from_network[0] = None
            requests_before_submit = request_count[0]
            print(f"   Số requests trước khi submit: {requests_before_submit}", flush=True)
            
            # Gửi Enter key ngay
            textarea.press("Enter")
            # Đợi ngắn để request được gửi
            time.sleep(0.2)
            print(f"   Sau Enter - Requests: {request_count[0]}, Captured: {captured_payload_from_network[0] is not None}", flush=True)
            
            # Nếu vẫn không có sau 0.5s, thử Enter lần 2
            if not captured_payload_from_network[0]:
                time.sleep(0.3)
                if not captured_payload_from_network[0]:
                    print("   Thử gửi Enter lần 2...", flush=True)
                    textarea.press("Enter")
                    time.sleep(0.2)
                    print(f"   Sau Enter lần 2 - Requests: {request_count[0]}, Captured: {captured_payload_from_network[0] is not None}", flush=True)
            
            # Nếu vẫn không có, thử click submit button (fallback)
            if not captured_payload_from_network[0]:
                print("🔍 Thử tìm và click submit button...", flush=True)
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
                            print(f"✅ Đã click submit button với selector: {selector}", flush=True)
                            time.sleep(0.15)
                            print(f"   Sau click button - Requests: {request_count[0]}, Captured: {captured_payload_from_network[0] is not None}", flush=True)
                            break
                    except Exception as btn_err:
                        print(f"   Lỗi khi click button {selector}: {btn_err}", flush=True)
                        continue
            
            print(f"📤 Đã gửi message, đang chờ capture payload từ network request...", flush=True)
            print(f"   Tổng số requests hiện tại: {request_count[0]}", flush=True)
            capture_status["message"] = "Đang chờ capture payload từ network..."
            
            # Chờ payload được capture (tối đa 10 giây - request thường đến rất nhanh sau submit)
            max_wait = 10
            check_interval = 0.15  # Giảm interval xuống 150ms để check nhanh hơn
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
                    print(f"✅ Đã capture payload thành công!", flush=True)
                    print(f"   Tổng số requests: {request_count[0]}, Thời gian: {int(waited)}s", flush=True)
                    return payload
                
                # Log mỗi 2 giây để biết đang chờ
                if int(waited) % 2 == 0 and waited > 0:
                    print(f"   ⏳ Đang chờ... ({int(waited)}s/{max_wait}s) - Requests: {request_count[0]}, Captured: {captured_payload_from_network[0] is not None}", flush=True)
                
                time.sleep(check_interval)
                waited += check_interval
            
            # Nếu không capture được sau khi chờ
            print(f"❌ Không capture được sau {max_wait} giây", flush=True)
            print(f"   Tổng số requests: {request_count[0]}", flush=True)
            print(f"   Requests trước submit: {requests_before_submit}", flush=True)
            print(f"   Requests sau submit: {request_count[0] - requests_before_submit}", flush=True)
            raise Exception(f"Không tìm thấy network request POST đến {target_url} sau {max_wait} giây. Tổng requests: {request_count[0]}")
            
    except Exception as e:
        error_msg = f"Lỗi Playwright: {str(e)}"
        print(f"❌ {error_msg}", flush=True)
        import traceback
        traceback.print_exc()
        import sys
        sys.stdout.flush()
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
    
    print(f"🚀 Server đang khởi động tại: http://0.0.0.0:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
