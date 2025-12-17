"""
Script đơn giản để capture payload - có thể chạy độc lập
"""
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import time

# Thử import webdriver_manager
try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WEBDRIVER_MANAGER = True
except ImportError:
    USE_WEBDRIVER_MANAGER = False
    print("⚠️  webdriver-manager không được cài đặt. Sử dụng ChromeDriver thủ công.")
    print("💡 Chạy: pip install webdriver-manager")

def capture_payload(message="hi", output_file="payload.json"):
    """Capture payload từ Zapier chatbot"""
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = None
    try:
        print("🚀 Khởi tạo Chrome driver...")
        if USE_WEBDRIVER_MANAGER:
            try:
                # Sử dụng ChromeService với ChromeDriverManager (giống pattern trong code automation)
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ ChromeDriver đã được khởi tạo thành công")
            except Exception as e:
                print(f"⚠️  Lỗi webdriver-manager: {e}")
                print("🔄 Thử ChromeDriver mặc định...")
                try:
                    driver = webdriver.Chrome(options=chrome_options)
                    print("✅ ChromeDriver mặc định đã được khởi tạo thành công")
                except Exception as e2:
                    raise Exception(f"Không thể khởi tạo ChromeDriver: {e2}\nChạy: pip install --upgrade webdriver-manager")
        else:
            try:
                driver = webdriver.Chrome(options=chrome_options)
                print("✅ ChromeDriver đã được khởi tạo thành công")
            except Exception as e:
                raise Exception(f"Không thể khởi tạo ChromeDriver: {e}\nCài đặt: pip install webdriver-manager")
        
        # Inject script để capture
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                window.__capturedPayload = null;
                const originalFetch = window.fetch;
                window.fetch = function(...args) {
                    const url = args[0];
                    if (typeof url === 'string' && url.includes('/api/chat')) {
                        const [requestUrl, options] = args;
                        if (options && options.method === 'POST' && options.body) {
                            try {
                                window.__capturedPayload = JSON.parse(options.body);
                                console.log('✅ Captured:', window.__capturedPayload);
                            } catch (e) {}
                        }
                    }
                    return originalFetch.apply(this, args);
                };
            '''
        })
        
        url = "https://trungtamquanlykytucxadhquocgiahcm.zapier.app/"
        print(f"📡 Mở trang: {url}")
        driver.get(url)
        
        wait = WebDriverWait(driver, 20)
        
        # Tìm và nhập vào textarea
        selectors = [
            'textarea[placeholder*="Nhập"]',
            'textarea[placeholder*="câu hỏi"]',
            'textarea[data-testid*="prompt"]',
            'textarea',
        ]
        
        textarea = None
        for selector in selectors:
            try:
                textarea = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                break
            except:
                continue
        
        if not textarea:
            raise Exception("Không tìm thấy textarea")
        
        print(f"⌨️  Nhập: '{message}'")
        textarea.clear()
        textarea.send_keys(message)
        time.sleep(0.3)
        
        # Gửi bằng Enter
        textarea.send_keys(Keys.RETURN)
        print("📤 Đã gửi, chờ capture...")
        
        # Chờ capture (10 giây)
        for i in range(20):
            payload = driver.execute_script("return window.__capturedPayload;")
            if payload:
                print("✅ Đã capture thành công!")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(payload, f, indent=2, ensure_ascii=False)
                print(f"💾 Đã lưu vào: {output_file}")
                return payload
            time.sleep(0.5)
        
        raise TimeoutException("Timeout: Không capture được payload")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return None
    finally:
        if driver:
            print("🔒 Đóng browser...")
            driver.quit()

if __name__ == "__main__":
    import sys
    message = sys.argv[1] if len(sys.argv) > 1 else "hi"
    capture_payload(message)

