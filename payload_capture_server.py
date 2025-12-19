"""
Payload Capture Server - Tự động capture payload từ Zapier chatbot
Sử dụng Playwright thay vì Selenium (nhẹ hơn, dễ cài hơn)
Tích hợp Firebase Firestore để quản lý payloads
"""
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import json
import time
import threading
import os
import requests
import uuid
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Firebase Admin SDK
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("⚠️  Firebase Admin SDK not installed. Install with: pip install firebase-admin")

app = Flask(__name__)
CORS(app)

# Initialize Firebase Admin SDK
def init_firebase():
    """Khởi tạo Firebase Admin SDK"""
    if not FIREBASE_AVAILABLE:
        return None
    
    try:
        # Kiểm tra xem đã initialize chưa
        if not firebase_admin._apps:
            # Cách 1: Dùng JSON string từ environment variable (khuyến nghị cho production)
            if os.environ.get('FIREBASE_CREDENTIALS_JSON'):
                cred_json = json.loads(os.environ.get('FIREBASE_CREDENTIALS_JSON'))
                cred = credentials.Certificate(cred_json)
                firebase_admin.initialize_app(cred)
                print("✅ Firebase initialized from JSON string")
            # Cách 2: Dùng service account key file (JSON)
            elif os.environ.get('FIREBASE_CREDENTIALS_PATH') and os.path.exists(os.environ.get('FIREBASE_CREDENTIALS_PATH')):
                cred = credentials.Certificate(os.environ.get('FIREBASE_CREDENTIALS_PATH'))
                firebase_admin.initialize_app(cred)
                print("✅ Firebase initialized from credentials file")
            # Cách 3: Dùng default credentials (Google Cloud)
            else:
                try:
                    firebase_admin.initialize_app()
                    print("✅ Firebase initialized with default credentials")
                except Exception as e:
                    print(f"⚠️  Firebase initialization failed: {e}")
                    return None
            
            # Test connection
            db = firestore.client()
            # Test read (count documents)
            test_ref = db.collection('_test').limit(1).stream()
            list(test_ref)  # Force query execution
            print("✅ Firebase Firestore connection OK")
            
        return firestore.client()
    except Exception as e:
        print(f"❌ Error initializing Firebase: {e}")
        import traceback
        traceback.print_exc()
        return None

# Initialize Firebase
db = init_firebase()

# Helper functions
def get_or_create_user_id(user_id=None):
    """Tạo hoặc lấy user_id"""
    if user_id:
        return user_id
    return f"user_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"

# Global variables để lưu payload (giữ lại cho backward compatibility)
captured_payload = None
capture_status = {
    "status": "idle",  # idle, capturing, captured, error
    "payload": None,
    "error": None
}

def capture_and_save_payload_to_firestore(initial_message="hi", save_to_firestore=True):
    """Capture payload và lưu vào Firestore (dùng cho background task)"""
    if not db and save_to_firestore:
        print("❌ Firebase not initialized, cannot save to Firestore")
        return None
    
    try:
        print("🚀 [Auto-refill] Khởi tạo Playwright browser...", flush=True)
        
        with sync_playwright() as p:
            print(f"🌐 [Auto-refill] Đang khởi động browser (headless mode)...", flush=True)
            try:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-gpu',
                        '--disable-software-rasterizer',
                        '--disable-extensions',
                    ],
                )
            except Exception as launch_err:
                error_str = str(launch_err).lower()
                if "missing dependencies" in error_str or "host system is missing" in error_str:
                    print("❌ [Auto-refill] Missing system dependencies", flush=True)
                    raise Exception("Missing system dependencies")
                else:
                    raise
            
            context_options = {
                'viewport': {'width': 1920, 'height': 1080},
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            context = browser.new_context(**context_options)
            
            page = context.new_page()
            
            # Biến để lưu captured payload
            captured_payload_from_network = [None]
            request_count = [0]
            
            def handle_request(request):
                request_count[0] += 1
                if '/api/chat' in request.url and request.method == 'POST':
                    try:
                        post_data = request.post_data
                        if post_data:
                            if isinstance(post_data, str):
                                payload = json.loads(post_data)
                            elif isinstance(post_data, dict):
                                payload = post_data
                            else:
                                post_data_str = post_data.decode('utf-8') if isinstance(post_data, bytes) else str(post_data)
                                payload = json.loads(post_data_str)
                            
                            captured_payload_from_network[0] = payload
                            print(f"✅ [Auto-refill] Đã capture payload!", flush=True)
                    except Exception as e:
                        print(f"⚠️  [Auto-refill] Lỗi khi parse payload: {e}", flush=True)
            
            page.on("request", handle_request)
            
            url = "https://trungtamquanlykytucxadhquocgiahcm.zapier.app/"
            print(f"📡 [Auto-refill] Đang mở trang web: {url}", flush=True)
            
            # Load page
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
            except Exception:
                try:
                    page.goto(url, wait_until="commit", timeout=20000)
                    time.sleep(2)
                except Exception:
                    page.goto(url, wait_until="load", timeout=25000)
            
            # Tìm textarea
            textarea = None
            exact_placeholders = [
                'textarea[placeholder="Nhập câu hỏi"]',
                'textarea[placeholder*="Nhập câu hỏi"]',
                'input[placeholder="Nhập câu hỏi"]',
            ]
            
            for selector in exact_placeholders:
                try:
                    textarea = page.wait_for_selector(selector, timeout=8000, state="visible")
                    if textarea:
                        break
                except PlaywrightTimeoutError:
                    continue
                except Exception:
                    continue
            
            if not textarea:
                other_selectors = ['textarea[placeholder*="Nhập"]', 'textarea', 'input[type="text"]']
                for selector in other_selectors:
                    try:
                        textarea = page.wait_for_selector(selector, timeout=5000, state="visible")
                        if textarea:
                            break
                    except Exception:
                        continue
            
            if not textarea:
                raise Exception("Không tìm thấy textarea")
            
            textarea.scroll_into_view_if_needed()
            textarea.click()
            textarea.fill(initial_message)
            
            # Submit
            captured_payload_from_network[0] = None
            textarea.press("Enter")
            time.sleep(0.5)
            
            if not captured_payload_from_network[0]:
                textarea.press("Enter")
                time.sleep(0.5)
            
            # Chờ payload
            max_wait = 10
            waited = 0
            payload_result = None
            
            while waited < max_wait:
                if captured_payload_from_network[0]:
                    payload_result = captured_payload_from_network[0]
                    break
                
                time.sleep(0.2)
                waited += 0.2
            
            # Đóng browser
            try:
                browser.close()
            except:
                pass
            
            if payload_result:
                # Lưu vào Firestore nếu cần
                if save_to_firestore and db:
                    doc_ref = db.collection('payloads').document()
                    doc_ref.set({
                        'payload_data': json.dumps(payload_result, ensure_ascii=False),
                        'is_used': False,
                        'user_id': None,
                        'user_name': None,
                        'user_info': None,
                        'assigned_at': None,
                        'created_at': firestore.SERVER_TIMESTAMP,
                        'updated_at': firestore.SERVER_TIMESTAMP
                    })
                    print(f"✅ [Auto-refill] Đã lưu payload vào Firestore (ID: {doc_ref.id})", flush=True)
                
                return payload_result
            else:
                raise Exception("Timeout: Không capture được payload")
            
    except Exception as e:
        error_msg = f"Lỗi capture payload: {str(e)}"
        print(f"❌ [Auto-refill] {error_msg}", flush=True)
        import traceback
        traceback.print_exc()
        return None

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
            
            # Tìm textarea với placeholder "Nhập câu hỏi" - ưu tiên selector chính xác nhất
            textarea = None
            
            # Strategy 1: Tìm với placeholder chính xác "Nhập câu hỏi" (ưu tiên cao nhất)
            exact_placeholders = [
                'textarea[placeholder="Nhập câu hỏi"]',  # Chính xác
                'textarea[placeholder*="Nhập câu hỏi"]',  # Contains
                'input[placeholder="Nhập câu hỏi"]',
                'input[placeholder*="Nhập câu hỏi"]',
            ]
            
            for selector in exact_placeholders:
                try:
                    print(f"   🔍 Đang thử selector (ưu tiên): {selector}", flush=True)
                    textarea = page.wait_for_selector(selector, timeout=8000, state="visible")
                    if textarea:
                        # Verify placeholder để chắc chắn
                        placeholder = textarea.get_attribute('placeholder') or ''
                        print(f"✅ Tìm thấy input với selector: {selector}", flush=True)
                        print(f"   Placeholder: '{placeholder}'", flush=True)
                        break
                except PlaywrightTimeoutError:
                    print(f"   ⏭️  Selector '{selector}' không tìm thấy, thử tiếp...", flush=True)
                    continue
                except Exception as e:
                    print(f"   ⚠️  Lỗi khi thử selector '{selector}': {e}", flush=True)
                    continue
            
            # Strategy 2: Nếu không tìm thấy với placeholder chính xác, thử các selector khác
            if not textarea:
                print("⚠️  Không tìm thấy với placeholder chính xác, thử các selector khác...", flush=True)
                other_selectors = [
                    'textarea[placeholder*="Nhập"]',
                    'textarea[placeholder*="câu hỏi"]',
                    'textarea[data-testid*="prompt"]',
                    'textarea[data-testid*="input"]',
                    'textarea[aria-label*="Nhập"]',
                    'textarea',
                    'input[type="text"][placeholder*="Nhập"]',
                    'input[type="text"]'
                ]
                
                for selector in other_selectors:
                    try:
                        print(f"   🔍 Đang thử selector: {selector}", flush=True)
                        textarea = page.wait_for_selector(selector, timeout=5000, state="visible")
                        if textarea:
                            placeholder = textarea.get_attribute('placeholder') or ''
                            print(f"✅ Tìm thấy input với selector: {selector}", flush=True)
                            print(f"   Placeholder: '{placeholder}'", flush=True)
                            break
                    except PlaywrightTimeoutError:
                        print(f"   ⏭️  Selector '{selector}' không tìm thấy, thử tiếp...", flush=True)
                        continue
                    except Exception as e:
                        print(f"   ⚠️  Lỗi khi thử selector '{selector}': {e}", flush=True)
                        continue
            
            # Strategy 3: Fallback - query_selector_all và filter theo placeholder
            if not textarea:
                print("⚠️  Không tìm thấy với wait_for_selector, thử query_selector_all và filter...", flush=True)
                all_textareas = page.query_selector_all('textarea, input[type="text"]')
                print(f"   Tìm thấy {len(all_textareas)} textarea/input elements", flush=True)
                
                # Ưu tiên element có placeholder chứa "Nhập câu hỏi"
                for elem in all_textareas:
                    try:
                        placeholder = elem.get_attribute('placeholder') or ''
                        print(f"   Element placeholder: '{placeholder}'", flush=True)
                        if 'Nhập câu hỏi' in placeholder or 'Nhập' in placeholder:
                            textarea = elem
                            print(f"✅ Sử dụng element có placeholder phù hợp: '{placeholder}'", flush=True)
                            break
                    except Exception:
                        continue
                
                # Nếu vẫn không có, lấy element đầu tiên
                if not textarea and all_textareas:
                    textarea = all_textareas[0]
                    placeholder = textarea.get_attribute('placeholder') or ''
                    print(f"⚠️  Sử dụng element đầu tiên từ query_selector_all, placeholder: '{placeholder}'", flush=True)
            
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

# ========== Firebase Firestore API Endpoints ==========

@app.route('/api/request-payload', methods=['POST'])
def request_payload():
    """User request một payload chưa sử dụng"""
    if not db:
        return jsonify({
            "success": False,
            "message": "Firebase not initialized. Please configure FIREBASE_CREDENTIALS_JSON."
        }), 500
    
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        user_name = data.get('user_name', '')
        user_info = data.get('user_info', {})  # {room: "101"} hoặc {phone: "0123456789"}
        
        if not user_id:
            return jsonify({
                "success": False,
                "message": "user_id is required"
            }), 400
        
        # Tìm payload chưa sử dụng
        unused_payloads = db.collection('payloads').where('is_used', '==', False).limit(1).stream()
        
        payload_ref = None
        for payload_doc in unused_payloads:
            payload_ref = payload_doc
            break
        
        if not payload_ref:
            return jsonify({
                "success": False,
                "message": "Không còn payload nào khả dụng. Vui lòng liên hệ admin."
            }), 404
        
        # Update payload với transaction để đảm bảo atomic
        transaction = db.transaction()
        payload_doc_ref = db.collection('payloads').document(payload_ref.id)
        
        @firestore.transactional
        def update_payload(transaction, doc_ref):
            snapshot = doc_ref.get(transaction=transaction)
            if not snapshot.exists:
                raise ValueError("Payload không tồn tại")
            
            data = snapshot.to_dict()
            if data.get('is_used', False):
                raise ValueError("Payload đã được sử dụng")
            
            # Update payload
            transaction.update(doc_ref, {
                'is_used': True,
                'user_id': user_id,
                'user_name': user_name,
                'user_info': user_info,
                'assigned_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            return data
        
        try:
            payload_data = update_payload(transaction, payload_doc_ref)
            payload_dict = json.loads(payload_data['payload_data']) if isinstance(payload_data.get('payload_data'), str) else payload_data.get('payload_data', {})
            
            return jsonify({
                "success": True,
                "payload": payload_dict,
                "payload_id": payload_ref.id,
                "user_id": user_id,
                "user_name": user_name,
                "user_info": user_info
            })
        except ValueError as e:
            # Payload đã được sử dụng, thử tìm payload khác
            return jsonify({
                "success": False,
                "message": "Payload đã được sử dụng, vui lòng thử lại."
            }), 409
        
    except Exception as e:
        print(f"❌ Error in request_payload: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Lỗi khi request payload: {str(e)}"
        }), 500

@app.route('/api/user/payload', methods=['GET'])
def get_user_payload():
    """Kiểm tra xem user đã có payload chưa"""
    if not db:
        return jsonify({
            "success": False,
            "message": "Firebase not initialized"
        }), 500
    
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                "success": False,
                "message": "user_id is required"
            }), 400
        
        # Tìm payload của user
        user_payloads = db.collection('payloads').where('user_id', '==', user_id).where('is_used', '==', True).limit(1).stream()
        
        for payload_doc in user_payloads:
            payload_data = payload_doc.to_dict()
            payload_dict = json.loads(payload_data['payload_data']) if isinstance(payload_data.get('payload_data'), str) else payload_data.get('payload_data', {})
            
            assigned_at = payload_data.get('assigned_at')
            if assigned_at and hasattr(assigned_at, 'isoformat'):
                assigned_at_str = assigned_at.isoformat()
            elif assigned_at:
                assigned_at_str = str(assigned_at)
            else:
                assigned_at_str = None
            
            return jsonify({
                "success": True,
                "has_payload": True,
                "payload": payload_dict,
                "user_name": payload_data.get('user_name'),
                "user_info": payload_data.get('user_info'),
                "assigned_at": assigned_at_str
            })
        
        return jsonify({
            "success": True,
            "has_payload": False
        })
            
    except Exception as e:
        print(f"❌ Error in get_user_payload: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Lỗi: {str(e)}"
        }), 500

@app.route('/api/admin/init-payloads', methods=['POST'])
def init_payloads_endpoint():
    """Init payloads qua API - Chạy 1 lần sau khi deploy"""
    if not db:
        return jsonify({
            "success": False,
            "message": "Firebase not initialized"
        }), 500
    
    try:
        admin_key = request.headers.get('X-Admin-Key') or (request.json or {}).get('admin_key')
        expected_key = os.environ.get('ADMIN_KEY', 'change-me-in-production')
        
        if admin_key != expected_key:
            return jsonify({
                "success": False,
                "message": "Unauthorized"
            }), 401
        
        count = (request.json or {}).get('count', 100)
        
        # Check xem đã có payloads chưa
        existing_count = len(list(db.collection('payloads').limit(1).stream()))
        if existing_count > 0:
            total_count = len(list(db.collection('payloads').stream()))
            return jsonify({
                "success": False,
                "message": f"Đã có {total_count} payloads. Xóa dữ liệu cũ trước khi tạo mới.",
                "existing_count": total_count
            }), 400
        
        base_payload = {
            "blockId": "cmgstldjf006hutqk4mroyx4o",
            "params": {
                "params": {
                    "projectSlug": "trungtamquanlykytucxadhquocgiahcm",
                    "pageId": "cmgstldib006futqk8rv7ro4u",
                    "chatbotId": "cmgstldjf006hutqk4mroyx4o"
                }
            },
            "stream": True,
            "useLegacyStreamFormat": True,
            "message": {
                "content": "",
                "role": "user"
            },
            "mode": "public"
        }
        
        created = []
        batch = db.batch()
        batch_count = 0
        
        for i in range(count):
            payload = base_payload.copy()
            unique_id = uuid.uuid4().hex[:15]
            payload["id"] = f"cm{unique_id}{i:03d}"
            payload["chatbotSessionId"] = f"cm{unique_id}{i:03d}"
            payload["predictionId"] = str(uuid.uuid4())
            
            # Create document reference
            doc_ref = db.collection('payloads').document()
            
            # Add to batch (Firestore batch limit: 500 operations)
            batch.set(doc_ref, {
                'payload_data': json.dumps(payload, ensure_ascii=False),
                'is_used': False,
                'user_id': None,
                'user_name': None,
                'user_info': None,
                'assigned_at': None,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            created.append(doc_ref.id)
            batch_count += 1
            
            # Firestore batch limit is 500, commit và tạo batch mới
            if batch_count >= 500:
                batch.commit()
                print(f"Created {i + 1}/{count} payloads...")
                batch = db.batch()
                batch_count = 0
        
        # Commit batch cuối cùng
        if batch_count > 0:
            batch.commit()
        
        print(f"✅ Created {count} payloads successfully!")
        
        return jsonify({
            "success": True,
            "message": f"Đã tạo {count} payloads thành công",
            "count": count,
            "created_ids": created[:10]  # Chỉ trả về 10 ID đầu
        })
        
    except Exception as e:
        print(f"❌ Error in init_payloads: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Lỗi: {str(e)}"
        }), 500

@app.route('/api/admin/payloads', methods=['GET'])
def list_payloads():
    """Admin endpoint: Xem danh sách payloads"""
    if not db:
        return jsonify({
            "success": False,
            "message": "Firebase not initialized"
        }), 500
    
    try:
        admin_key = request.headers.get('X-Admin-Key')
        expected_key = os.environ.get('ADMIN_KEY', 'change-me-in-production')
        
        if admin_key != expected_key:
            return jsonify({
                "success": False,
                "message": "Unauthorized"
            }), 401
        
        is_used = request.args.get('is_used')  # 'true' hoặc 'false'
        limit = int(request.args.get('limit', 100))
        
        query = db.collection('payloads')
        if is_used is not None:
            query = query.where('is_used', '==', is_used.lower() == 'true')
        
        payloads = []
        for doc in query.order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit).stream():
            data = doc.to_dict()
            payload_dict = json.loads(data['payload_data']) if isinstance(data.get('payload_data'), str) else data.get('payload_data')
            
            assigned_at = data.get('assigned_at')
            created_at = data.get('created_at')
            
            assigned_at_str = assigned_at.isoformat() if assigned_at and hasattr(assigned_at, 'isoformat') else (str(assigned_at) if assigned_at else None)
            created_at_str = created_at.isoformat() if created_at and hasattr(created_at, 'isoformat') else (str(created_at) if created_at else None)
            
            payloads.append({
                'id': doc.id,
                'payload': payload_dict,
                'is_used': data.get('is_used', False),
                'user_id': data.get('user_id'),
                'user_name': data.get('user_name'),
                'user_info': data.get('user_info'),
                'assigned_at': assigned_at_str,
                'created_at': created_at_str
            })
        
        return jsonify({
            "success": True,
            "count": len(payloads),
            "payloads": payloads
        })
        
    except Exception as e:
        print(f"❌ Error in list_payloads: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Lỗi: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint - kiểm tra cả Firebase"""
    try:
        if db:
            # Test Firebase connection
            test_ref = db.collection('_test').limit(1).stream()
            list(test_ref)
            firebase_status = "ok"
            
            # Đếm payloads
            unused_count = len(list(db.collection('payloads').where('is_used', '==', False).stream()))
            total_count = len(list(db.collection('payloads').stream()))
            used_count = total_count - unused_count
        else:
            firebase_status = "not_initialized"
            unused_count = 0
            total_count = 0
            used_count = 0
    except Exception as e:
        firebase_status = f"error: {str(e)}"
        unused_count = 0
        total_count = 0
        used_count = 0
    
    return jsonify({
        "status": "ok",
        "firebase": firebase_status,
        "payloads": {
            "total": total_count,
            "unused": unused_count,
            "used": used_count
        },
        "background_task": "running" if background_thread and background_thread.is_alive() else "not_running"
    })

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

# ========== Background Task: Tự động kiểm tra và refill payloads ==========

def check_and_refill_payloads():
    """Kiểm tra số lượng payload và tự động capture nếu cần"""
    if not db:
        print("⚠️  [Auto-refill] Firebase not initialized, skipping check")
        return
    
    try:
        # Đếm số payload chưa sử dụng
        unused_payloads = list(db.collection('payloads').where('is_used', '==', False).stream())
        unused_count = len(unused_payloads)
        
        # Target: giữ 100 payloads
        TARGET_COUNT = 100
        MIN_THRESHOLD = 50  # Bắt đầu refill nếu dưới 50
        
        print(f"📊 [Auto-refill] Kiểm tra payloads: {unused_count}/{TARGET_COUNT} payloads chưa sử dụng", flush=True)
        
        if unused_count < MIN_THRESHOLD:
            needed = TARGET_COUNT - unused_count
            print(f"🔄 [Auto-refill] Bắt đầu capture {needed} payloads mới...", flush=True)
            
            success_count = 0
            failed_count = 0
            max_attempts = needed + 20  # Capture thêm 20 cái để có buffer
            
            for i in range(max_attempts):
                try:
                    print(f"🔄 [Auto-refill] Đang capture payload #{i+1}/{max_attempts}...", flush=True)
                    payload = capture_and_save_payload_to_firestore(initial_message="hi", save_to_firestore=True)
                    
                    if payload:
                        success_count += 1
                        print(f"✅ [Auto-refill] Thành công: {success_count}/{needed}", flush=True)
                        
                        # Kiểm tra lại số lượng
                        current_unused = len(list(db.collection('payloads').where('is_used', '==', False).stream()))
                        if current_unused >= TARGET_COUNT:
                            print(f"✅ [Auto-refill] Đã đủ {current_unused} payloads, dừng capture", flush=True)
                            break
                        
                        # Delay giữa các lần capture để tránh quá tải
                        time.sleep(3)
                    else:
                        failed_count += 1
                        print(f"❌ [Auto-refill] Thất bại: {failed_count} lần", flush=True)
                        
                        # Nếu fail nhiều lần liên tiếp, dừng lại
                        if failed_count >= 5:
                            print(f"⚠️  [Auto-refill] Thất bại quá nhiều lần, dừng capture", flush=True)
                            break
                        
                        time.sleep(5)  # Đợi lâu hơn nếu fail
                        
                except Exception as e:
                    failed_count += 1
                    print(f"❌ [Auto-refill] Lỗi khi capture: {e}", flush=True)
                    
                    if failed_count >= 5:
                        print(f"⚠️  [Auto-refill] Thất bại quá nhiều lần, dừng capture", flush=True)
                        break
                    
                    time.sleep(5)
            
            final_count = len(list(db.collection('payloads').where('is_used', '==', False).stream()))
            print(f"✅ [Auto-refill] Hoàn thành! Tổng payloads: {final_count}, Thành công: {success_count}, Thất bại: {failed_count}", flush=True)
        else:
            print(f"✅ [Auto-refill] Đủ payloads ({unused_count}/{TARGET_COUNT}), không cần capture thêm", flush=True)
            
    except Exception as e:
        print(f"❌ [Auto-refill] Lỗi khi kiểm tra và refill payloads: {e}", flush=True)
        import traceback
        traceback.print_exc()

def keep_alive_ping_task():
    """Background task để tự động ping keep-alive endpoint mỗi 10 phút để tránh spin down"""
    PING_INTERVAL = 600  # 10 phút = 600 giây
    
    # Chờ server khởi động xong
    time.sleep(30)
    
    print(f"💓 [Keep-alive] Keep-alive ping task đã khởi động, sẽ ping mỗi {PING_INTERVAL/60} phút", flush=True)
    
    while True:
        try:
            # Ping keep-alive endpoint để giữ service không bị spin down
            import urllib.request
            import urllib.error
            
            try:
                # Lấy PORT từ environment hoặc dùng default
                port = int(os.environ.get('PORT', 5000))
                # Ping localhost (service đang chạy trên cùng instance)
                url = f"http://localhost:{port}/keep-alive"
                
                with urllib.request.urlopen(url, timeout=5) as response:
                    if response.status == 200:
                        print(f"💓 [Keep-alive] Ping thành công - Service đang hoạt động", flush=True)
            except Exception as ping_err:
                # Không log lỗi vì có thể service chưa sẵn sàng
                pass
                
        except Exception as e:
            # Không log lỗi để tránh spam logs
            pass
        
        # Đợi PING_INTERVAL giây trước khi ping lần tiếp theo
        time.sleep(PING_INTERVAL)

def background_refill_task():
    """Background task chạy mỗi 1 giờ để kiểm tra và refill payloads"""
    CHECK_INTERVAL = 3600  # 1 giờ = 3600 giây
    
    # Chờ một chút sau khi server khởi động
    time.sleep(60)  # Đợi 1 phút sau khi server start
    
    print(f"🔄 [Auto-refill] Background task đã khởi động, sẽ kiểm tra mỗi {CHECK_INTERVAL/60} phút", flush=True)
    
    while True:
        try:
            check_and_refill_payloads()
        except Exception as e:
            print(f"❌ [Auto-refill] Lỗi trong background task: {e}", flush=True)
        
        # Đợi CHECK_INTERVAL giây trước khi kiểm tra lần tiếp theo
        print(f"⏰ [Auto-refill] Đợi {CHECK_INTERVAL/60} phút trước khi kiểm tra lần tiếp theo...", flush=True)
        time.sleep(CHECK_INTERVAL)

# Global variable để track background thread
background_thread = None

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"🚀 Server đang khởi động tại: http://0.0.0.0:{port}")
    
    # Khởi động keep-alive ping task (luôn chạy để tránh spin down)
    keep_alive_thread = threading.Thread(target=keep_alive_ping_task, daemon=True)
    keep_alive_thread.start()
    print("✅ Keep-alive ping task đã được khởi động (ping mỗi 10 phút)")
    
    # Khởi động background task trong thread riêng
    if db:
        background_thread = threading.Thread(target=background_refill_task, daemon=True)
        background_thread.start()
        print("✅ Background auto-refill task đã được khởi động")
    else:
        print("⚠️  Firebase not initialized, background auto-refill task sẽ không chạy")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
