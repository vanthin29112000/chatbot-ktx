"""
Script để update ChromeDriver và xóa cache
"""
import os
import shutil
import subprocess
import sys

def get_cache_dir():
    """Lấy đường dẫn cache webdriver-manager"""
    return os.path.join(os.path.expanduser("~"), ".wdm")

def clear_cache():
    """Xóa cache webdriver-manager"""
    cache_dir = get_cache_dir()
    if os.path.exists(cache_dir):
        try:
            print(f"🧹 Đang xóa cache tại: {cache_dir}")
            shutil.rmtree(cache_dir)
            print("✅ Đã xóa cache thành công!")
            return True
        except Exception as e:
            print(f"❌ Lỗi khi xóa cache: {e}")
            return False
    else:
        print("ℹ️  Không tìm thấy cache để xóa")
        return True

def update_webdriver_manager():
    """Cập nhật webdriver-manager lên version mới nhất"""
    try:
        print("📦 Đang cập nhật webdriver-manager...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "webdriver-manager"])
        print("✅ Đã cập nhật webdriver-manager thành công!")
        return True
    except Exception as e:
        print(f"❌ Lỗi khi cập nhật: {e}")
        return False

def test_chromedriver():
    """Test xem ChromeDriver có hoạt động không"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("🧪 Đang test ChromeDriver...")
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://www.google.com")
        print(f"✅ ChromeDriver hoạt động tốt! Title: {driver.title}")
        driver.quit()
        return True
    except Exception as e:
        print(f"❌ Lỗi khi test ChromeDriver: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 CHROME DRIVER UPDATER")
    print("=" * 60)
    print()
    
    # Bước 1: Xóa cache
    print("Bước 1: Xóa cache webdriver-manager")
    clear_cache()
    print()
    
    # Bước 2: Update webdriver-manager
    print("Bước 2: Cập nhật webdriver-manager")
    update_webdriver_manager()
    print()
    
    # Bước 3: Test
    print("Bước 3: Test ChromeDriver")
    if test_chromedriver():
        print()
        print("=" * 60)
        print("✅ HOÀN TẤT! ChromeDriver đã được cập nhật và hoạt động tốt.")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("⚠️  VẪN CÒN LỖI")
        print("=" * 60)
        print("\n💡 Thử các giải pháp sau:")
        print("1. Kiểm tra Chrome version: chrome://version")
        print("2. Tải ChromeDriver thủ công từ:")
        print("   https://googlechromelabs.github.io/chrome-for-testing/")
        print("3. Đặt ChromeDriver vào PATH")

