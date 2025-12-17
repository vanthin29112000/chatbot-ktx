"""
Payload Capture Server - Tự động capture payload từ Zapier chatbot
Sử dụng Selenium để tự động hóa quy trình
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException

# Thử import webdriver_manager, nếu không có thì dùng ChromeDriver thủ công
try:
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service as ChromeService
    USE_WEBDRIVER_MANAGER = True
except ImportError:
    USE_WEBDRIVER_MANAGER = False
    print("⚠️  webdriver-manager không được cài đặt. Sử dụng ChromeDriver thủ công.")
    print("💡 Chạy: pip install webdriver-manager để tự động quản lý ChromeDriver")

app = Flask(__name__)
CORS(app)

# Global variables để lưu payload
captured_payload = None
capture_status = {
    "status": "idle",  # idle, capturing, captured, error
    "payload": None,
    "error": None
}

def capture_payload_selenium(initial_message="hi"):
    """Sử dụng Selenium để tự động capture payload"""
    global captured_payload, capture_status
    
    capture_status["status"] = "capturing"
    capture_status["error"] = None
    
    driver = None
    try:
        # Cấu hình Chrome options - HEADLESS MODE (ẩn browser)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Bật headless để ẩn browser
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--window-size=1920,1080")  # Set kích thước cửa sổ cho headless
        chrome_options.add_argument("--disable-gpu")  # Tắt GPU cho headless mode
        
        # Bật logging để capture network requests
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        print("🚀 Khởi tạo Chrome driver...")
        capture_status["message"] = "Đang khởi tạo trình duyệt..."
        if USE_WEBDRIVER_MANAGER:
            try:
                # Xóa cache để đảm bảo tải ChromeDriver mới nhất (tương thích với Chrome hiện tại)
                import os
                cache_dir = os.path.join(os.path.expanduser("~"), ".wdm")
                if os.path.exists(cache_dir):
                    print("🧹 Đang xóa cache webdriver-manager để tải ChromeDriver mới...")
                    import shutil
                    try:
                        shutil.rmtree(cache_dir)
                        print("✅ Đã xóa cache thành công")
                    except Exception as cache_error:
                        print(f"⚠️  Không thể xóa cache: {cache_error}")
                
                # Sử dụng ChromeService với ChromeDriverManager (giống như code automation của bạn)
                # driver_version="LATEST" để đảm bảo tải version mới nhất
                print("📥 Đang tải ChromeDriver mới nhất...")
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ ChromeDriver đã được khởi tạo thành công")
            except Exception as e:
                error_str = str(e)
                print(f"⚠️  Lỗi khi dùng webdriver-manager: {e}")
                
                # Kiểm tra nếu là lỗi version mismatch
                if "only supports Chrome version" in error_str or "This version of ChromeDriver" in error_str:
                    print("🔧 Phát hiện lỗi version mismatch, đang cố gắng fix...")
                    # Thử xóa cache và tải lại
                    import os
                    import shutil
                    cache_dir = os.path.join(os.path.expanduser("~"), ".wdm")
                    if os.path.exists(cache_dir):
                        try:
                            shutil.rmtree(cache_dir)
                            print("✅ Đã xóa cache, thử tải lại ChromeDriver...")
                            service = ChromeService(ChromeDriverManager().install())
                            driver = webdriver.Chrome(service=service, options=chrome_options)
                            print("✅ ChromeDriver đã được khởi tạo thành công sau khi xóa cache")
                        except Exception as retry_error:
                            error_msg = f"Lỗi version mismatch ChromeDriver:\n{error_str}\n\n"
                            error_msg += "💡 Giải pháp:\n"
                            error_msg += "1. Cập nhật webdriver-manager: pip install --upgrade webdriver-manager\n"
                            error_msg += "2. Xóa cache thủ công: xóa thư mục %USERPROFILE%\\.wdm\n"
                            error_msg += "3. Hoặc tải ChromeDriver thủ công cho Chrome 143 từ:\n"
                            error_msg += "   https://googlechromelabs.github.io/chrome-for-testing/\n"
                            raise Exception(error_msg)
                    else:
                        raise
                else:
                    print("🔄 Thử dùng ChromeDriver mặc định...")
                    try:
                        driver = webdriver.Chrome(options=chrome_options)
                        print("✅ ChromeDriver mặc định đã được khởi tạo thành công")
                    except Exception as e2:
                        error_msg = f"Lỗi khởi tạo ChromeDriver: {str(e2)}\n"
                        error_msg += "💡 Giải pháp:\n"
                        error_msg += "1. Đảm bảo Chrome đã được cài đặt\n"
                        error_msg += "2. Chạy: pip install --upgrade webdriver-manager selenium\n"
                        error_msg += "3. Xóa cache: xóa thư mục .wdm trong user home\n"
                        error_msg += "4. Hoặc tải ChromeDriver thủ công từ: https://chromedriver.chromium.org/\n"
                        error_msg += "5. Đặt ChromeDriver vào PATH hoặc cùng thư mục với script"
                        raise Exception(error_msg)
        else:
            try:
                driver = webdriver.Chrome(options=chrome_options)
                print("✅ ChromeDriver đã được khởi tạo thành công")
            except Exception as e:
                error_msg = f"Lỗi khởi tạo ChromeDriver: {str(e)}\n"
                error_msg += "💡 Giải pháp:\n"
                error_msg += "1. Cài đặt: pip install webdriver-manager\n"
                error_msg += "2. Hoặc tải ChromeDriver thủ công và đặt vào PATH"
                raise Exception(error_msg)
        
        # Enable Network domain để lắng nghe network requests
        print("🔍 Đang bật Network domain để capture requests...")
        driver.execute_cdp_cmd('Network.enable', {})
        
        # Biến để lưu captured payload từ network
        captured_payload_from_network = [None]
        
        # URL mục tiêu cần capture
        target_url = "https://trungtamquanlykytucxadhquocgiahcm.zapier.app/api/chat"
        
        print(f"✅ Đã bật Network domain, sẽ capture requests đến: {target_url}")
        
        url = "https://trungtamquanlykytucxadhquocgiahcm.zapier.app/"
        print(f"📡 Đang mở trang web: {url}")
        capture_status["message"] = "Đang truy cập trang web..."
        driver.get(url)
        
        # Chờ trang load - tăng thời gian chờ cho headless mode
        wait = WebDriverWait(driver, 30)
        print("⏳ Đang chờ trang web load...")
        capture_status["message"] = "Đang chờ trang web load..."
        
        # Đợi thêm một chút để trang load hoàn toàn
        time.sleep(2)
        
        # Đợi document ready
        try:
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("✅ Trang web đã load xong")
        except:
            pass
        
        capture_status["message"] = "Đang tìm input field..."
        
        # Tìm textarea để nhập message
        try:
            # Thử tìm textarea với nhiều selector khác nhau
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
                    # Chờ element vừa present vừa clickable (có thể tương tác)
                    textarea = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    print(f"✅ Tìm thấy input với selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not textarea:
                raise Exception("Không tìm thấy textarea để nhập message")
            
            # Scroll element vào view để đảm bảo có thể tương tác
            try:
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", textarea)
                time.sleep(0.5)
            except:
                pass
            
            # Đợi thêm một chút để đảm bảo element sẵn sàng
            time.sleep(1)
            
            # Nhập message
            print(f"⌨️  Đang nhập message: '{initial_message}'")
            capture_status["message"] = "Đang nhập message..."
            
            # Thử nhiều cách để nhập text
            try:
                # Click và focus vào textarea trước
                textarea.click()
                time.sleep(0.2)
                textarea.clear()
                time.sleep(0.2)
                
                # Cách 1: Dùng send_keys để nhập (tự nhiên hơn, có thể trigger events)
                from selenium.webdriver.common.keys import Keys
                textarea.send_keys(initial_message)
                time.sleep(0.3)
                print("✅ Đã nhập message bằng send_keys")
                
                # Verify value đã được set
                actual_value = driver.execute_script("return arguments[0].value;", textarea)
                print(f"✅ Verified textarea value: '{actual_value}'")
                
            except Exception as send_error:
                print(f"⚠️  Lỗi khi nhập bằng send_keys, thử cách khác: {send_error}")
                try:
                    # Cách 2: Dùng JavaScript để set value
                    escaped_message = json.dumps(initial_message)  # Escape JSON-safe
                    driver.execute_script(f"arguments[0].value = {escaped_message};", textarea)
                    # Trigger input event để trang web nhận biết
                    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", textarea)
                    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", textarea)
                    print("✅ Đã nhập message bằng JavaScript")
                    
                    # Verify value đã được set
                    actual_value = driver.execute_script("return arguments[0].value;", textarea)
                    print(f"✅ Verified textarea value: '{actual_value}'")
                except Exception as js_error:
                    print(f"⚠️  Lỗi khi nhập bằng JS, thử cách cuối: {js_error}")
                    # Cách 3: Dùng ActionChains
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(driver)
                    actions.move_to_element(textarea).click().send_keys(initial_message).perform()
                    print("✅ Đã nhập message bằng ActionChains")
            
            # Đợi một chút để value được xử lý
            time.sleep(0.5)
            
            # Đảm bảo textarea vẫn focused
            try:
                driver.execute_script("arguments[0].focus();", textarea)
                time.sleep(0.2)
            except:
                pass
            
            # Clear performance logs trước khi submit để chỉ lấy logs mới
            try:
                driver.get_log('performance')  # Clear logs
                print("✅ Đã clear performance logs trước khi submit")
            except:
                pass
            
            # Submit form - ƯU TIÊN GỬI ENTER KEY TRƯỚC (cách đơn giản và hiệu quả nhất)
            submitted = False
            from selenium.webdriver.common.keys import Keys
            
            # Cách 1: Gửi Enter key trực tiếp vào textarea (CÁCH CHÍNH)
            print("⌨️  Đang gửi Enter key để submit form...")
            
            # Đảm bảo textarea được focus
            try:
                textarea.click()
                time.sleep(0.2)
                # Verify focus
                is_focused = driver.execute_script("return document.activeElement === arguments[0];", textarea)
                print(f"🔍 Textarea focused: {is_focused}")
            except:
                pass
            
            try:
                # Gửi Enter key nhiều lần để đảm bảo
                print("⌨️  Gửi Enter key lần 1...")
                textarea.send_keys(Keys.RETURN)
                time.sleep(0.3)
                
                # Gửi thêm một lần nữa để chắc chắn
                print("⌨️  Gửi Enter key lần 2...")
                textarea.send_keys(Keys.RETURN)
                submitted = True
                print("✅ Đã gửi Enter key thành công")
                
            except Exception as enter_err:
                print(f"⚠️  Lỗi khi gửi Enter key bằng Selenium: {enter_err}")
                try:
                    # Fallback: Dùng JavaScript để gửi Enter với đầy đủ events
                    print("⌨️  Thử gửi Enter bằng JavaScript với đầy đủ events...")
                    driver.execute_script("""
                        var textarea = arguments[0];
                        textarea.focus();
                        
                        // Trigger keydown
                        var keydown = new KeyboardEvent('keydown', {
                            key: 'Enter',
                            code: 'Enter',
                            keyCode: 13,
                            which: 13,
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        textarea.dispatchEvent(keydown);
                        
                        // Trigger keypress
                        var keypress = new KeyboardEvent('keypress', {
                            key: 'Enter',
                            code: 'Enter',
                            keyCode: 13,
                            which: 13,
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        textarea.dispatchEvent(keypress);
                        
                        // Trigger keyup
                        var keyup = new KeyboardEvent('keyup', {
                            key: 'Enter',
                            code: 'Enter',
                            keyCode: 13,
                            which: 13,
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        textarea.dispatchEvent(keyup);
                        
                        // Thử submit form nếu có
                        var form = textarea.closest('form');
                        if (form) {
                            form.requestSubmit();
                        }
                    """, textarea)
                    time.sleep(0.5)
                    submitted = True
                    print("✅ Đã gửi Enter bằng JavaScript")
                except Exception as js_enter_err:
                    print(f"⚠️  Lỗi khi gửi Enter bằng JavaScript: {js_enter_err}")
            
            # Cách 2: Tìm và click submit button (fallback)
            if not submitted:
                print("🔍 Thử tìm và click submit button...")
                submit_selectors = [
                    'button[type="submit"]',
                    'button:contains("Gửi")',
                    'button[aria-label*="Send"]',
                    'button[data-testid*="send"]',
                    'button:last-of-type',
                ]
                
                submit_button = None
                for selector in submit_selectors:
                    try:
                        if ':contains(' in selector:
                            # Xử lý XPath cho text content
                            submit_button = driver.find_element(By.XPATH, f"//button[contains(text(), 'Gửi')]")
                        else:
                            submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                        print(f"✅ Tìm thấy submit button với selector: {selector}")
                        break
                    except:
                        continue
                
                if submit_button:
                    try:
                        # Scroll button vào view và đợi clickable
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_button)
                        time.sleep(0.3)
                        # Chờ button enabled
                        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(submit_button))
                        submit_button.click()
                        submitted = True
                        print("✅ Đã click button bằng Selenium")
                    except:
                        try:
                            driver.execute_script("arguments[0].click();", submit_button)
                            submitted = True
                            print("✅ Đã click button bằng JavaScript")
                        except Exception as click_err:
                            print(f"⚠️  Lỗi khi click button: {click_err}")
            
            # Cách 3: Submit form trực tiếp (fallback cuối cùng)
            if not submitted:
                try:
                    form = textarea.find_element(By.XPATH, "./ancestor::form")
                    if form:
                        print("✅ Tìm thấy form, thử submit form...")
                        driver.execute_script("arguments[0].requestSubmit();", form)
                        submitted = True
                        print("✅ Đã submit form bằng requestSubmit()")
                except:
                    pass
            
            if not submitted:
                print("⚠️  Không thể submit form bằng bất kỳ cách nào")
            else:
                print("✅ Đã submit form thành công!")
            
            print(f"📤 Đã gửi message, đang chờ capture payload từ network request đến {target_url}...")
            capture_status["message"] = "Đang chờ capture payload từ network..."
            
            # Đợi một chút để request được gửi
            time.sleep(1)
            
            # Chờ payload được capture từ network requests (tối đa 20 giây)
            max_wait = 20
            check_interval = 0.3
            waited = 0
            
            print(f"🔍 Đang kiểm tra network requests đến {target_url}...")
            
            while waited < max_wait:
                # Kiểm tra performance logs để tìm network requests đến /api/chat
                try:
                    # Lấy performance logs
                    logs = driver.get_log('performance')
                    
                    # Tìm request gần nhất đến /api/chat (POST)
                    for log in reversed(logs):  # Duyệt từ cuối để lấy request mới nhất
                        try:
                            log_message = json.loads(log['message'])
                            message = log_message.get('message', {})
                            method = message.get('method', '')
                            
                            # Tìm requestWillBeSent event
                            if method == 'Network.requestWillBeSent':
                                params = message.get('params', {})
                                request_info = params.get('request', {})
                                request_url = request_info.get('url', '')
                                request_method = request_info.get('method', '')
                                
                                # Kiểm tra nếu là POST request đến target_url (check cả full URL và path)
                                is_target_url = (
                                    request_url == target_url or 
                                    request_url.startswith(target_url) or
                                    target_url in request_url or
                                    '/api/chat' in request_url
                                )
                                
                                if is_target_url and request_method == 'POST':
                                    print(f"🔍 Tìm thấy POST request đến target URL: {request_url}")
                                    
                                    # Lấy postData từ request
                                    post_data = request_info.get('postData', '')
                                    if post_data:
                                        try:
                                            payload = json.loads(post_data)
                                            
                                            # Lưu payload
                                            captured_payload_from_network[0] = payload
                                            captured_payload = payload
                                            capture_status["status"] = "captured"
                                            capture_status["payload"] = payload
                                            capture_status["message"] = "Hoàn thành!"
                                            print(f"✅ Đã capture payload từ network request!")
                                            print(f"📋 Request URL: {request_url}")
                                            print(f"📋 Request Method: {request_method}")
                                            print(f"📦 Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
                                            return payload
                                        except Exception as parse_err:
                                            print(f"⚠️  Lỗi parse postData: {parse_err}")
                                            print(f"⚠️  PostData (first 200 chars): {post_data[:200]}")
                                    else:
                                        # Nếu không có postData trong log, có thể cần lấy từ request headers/body khác
                                        print(f"⚠️  Tìm thấy POST request đến {request_url} nhưng không có postData trong log")
                                        print(f"⚠️  Request headers: {request_info.get('headers', {})}")
                                        
                                        # Thử lấy từ requestId và request body bằng cách khác
                                        request_id = params.get('requestId', '')
                                        if request_id:
                                            print(f"⚠️  RequestId: {request_id}")
                                            
                        except Exception as log_parse_err:
                            # Skip invalid log entries
                            continue
                
                except Exception as log_err:
                    # Có thể chưa có logs, tiếp tục đợi
                    pass
                
                # Debug log - in ra tất cả requests có chứa /api/chat
                if waited > 1 and int(waited * 10) % 20 == 0:
                    print(f"🔍 [Debug] Đang chờ network request POST đến {target_url}... Đã chờ: {waited:.1f}s")
                    # In ra tất cả requests có /api/chat để debug
                    try:
                        logs = driver.get_log('performance')
                        api_chat_requests = []
                        for log in logs:
                            try:
                                log_message = json.loads(log['message'])
                                message = log_message.get('message', {})
                                method = message.get('method', '')
                                if method == 'Network.requestWillBeSent':
                                    params = message.get('params', {})
                                    request_info = params.get('request', {})
                                    request_url = request_info.get('url', '')
                                    if '/api/chat' in request_url or target_url in request_url:
                                        api_chat_requests.append({
                                            'url': request_url,
                                            'method': request_info.get('method', ''),
                                            'hasPostData': bool(request_info.get('postData', ''))
                                        })
                            except:
                                pass
                        if api_chat_requests:
                            print(f"🔍 [Debug] Tìm thấy {len(api_chat_requests)} request(s) đến target URL:")
                            for req in api_chat_requests:
                                print(f"   - {req['method']} {req['url']} (có postData: {req['hasPostData']})")
                    except:
                        pass
                
                time.sleep(check_interval)
                waited += check_interval
            
            raise TimeoutException(f"Không tìm thấy network request POST đến {target_url} sau {max_wait} giây. Có thể message chưa được gửi thành công.")
            
        except Exception as e:
            error_msg = f"Lỗi khi tương tác với trang web: {str(e)}"
            print(f"❌ {error_msg}")
            capture_status["status"] = "error"
            capture_status["error"] = error_msg
            raise
            
    except Exception as e:
        error_msg = f"Lỗi Selenium: {str(e)}"
        print(f"❌ {error_msg}")
        capture_status["status"] = "error"
        capture_status["error"] = error_msg
        return None
        
    finally:
        global is_capturing
        if driver:
            print("🔒 Đang đóng browser...")
            try:
                driver.quit()
            except:
                pass
        
        # Reset flag sau khi hoàn thành
        with capture_lock:
            is_capturing = False

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
        
        # Chạy Selenium trong thread riêng để không block
        thread = threading.Thread(target=capture_payload_selenium, args=(initial_message,))
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
    global capture_status
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
    global is_capturing
    with capture_lock:
        is_capturing = False
    return jsonify({
        "success": True,
        "message": "Capture flag đã được reset"
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print("=" * 60)
    print("🚀 Payload Capture Server đang khởi động...")
    print("=" * 60)
    print("\n📝 HƯỚNG DẪN:")
    print("1. Đảm bảo đã cài đặt Chrome và ChromeDriver")
    print(f"2. Server sẽ chạy tại: http://0.0.0.0:{port}")
    print("3. React app sẽ gọi API này để capture payload tự động")
    print("\n" + "=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)