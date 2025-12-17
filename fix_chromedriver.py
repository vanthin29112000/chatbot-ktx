"""
Script để kiểm tra và sửa lỗi ChromeDriver
"""
import sys
import platform
import subprocess
import os

def get_chrome_version():
    """Lấy version của Chrome đã cài"""
    try:
        if platform.system() == "Windows":
            # Thử nhiều path Chrome trên Windows
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            ]
            for path in paths:
                if os.path.exists(path):
                    result = subprocess.run(
                        [path, "--version"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        version = result.stdout.strip().split()[-1]
                        major_version = version.split('.')[0]
                        return major_version
        elif platform.system() == "Darwin":  # macOS
            result = subprocess.run(
                ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                version = result.stdout.strip().split()[-1]
                return version.split('.')[0]
        else:  # Linux
            result = subprocess.run(
                ["google-chrome", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                version = result.stdout.strip().split()[-1]
                return version.split('.')[0]
    except Exception as e:
        print(f"❌ Không thể lấy Chrome version: {e}")
    return None

def check_chromedriver():
    """Kiểm tra ChromeDriver"""
    print("=" * 60)
    print("🔍 KIỂM TRA CHROMEDRIVER")
    print("=" * 60)
    
    # Kiểm tra hệ thống
    print(f"\n🖥️  Hệ điều hành: {platform.system()} {platform.machine()}")
    print(f"🐍 Python version: {sys.version}")
    
    # Kiểm tra Chrome
    chrome_version = get_chrome_version()
    if chrome_version:
        print(f"✅ Chrome version: {chrome_version}")
    else:
        print("❌ Không tìm thấy Chrome hoặc không thể đọc version")
        print("💡 Đảm bảo Chrome đã được cài đặt")
        return
    
    # Kiểm tra webdriver-manager
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ webdriver-manager đã được cài đặt")
        
        # Thử tải ChromeDriver
        print("\n📦 Đang tải ChromeDriver...")
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver đã được tải: {driver_path}")
        
        # Kiểm tra file
        if os.path.exists(driver_path):
            size = os.path.getsize(driver_path)
            print(f"📊 File size: {size:,} bytes")
            
            # Thử khởi tạo driver
            print("\n🧪 Kiểm tra khởi tạo driver...")
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            try:
                service = Service(driver_path)
                driver = webdriver.Chrome(service=service, options=options)
                driver.quit()
                print("✅ ChromeDriver hoạt động tốt!")
            except Exception as e:
                print(f"❌ Lỗi khi khởi tạo driver: {e}")
                print("\n💡 Giải pháp:")
                print("1. Xóa cache webdriver-manager:")
                print("   - Windows: %USERPROFILE%\\.wdm")
                print("   - Linux/Mac: ~/.wdm")
                print("2. Chạy lại: pip install --upgrade webdriver-manager")
                print("3. Hoặc tải ChromeDriver thủ công từ:")
                print(f"   https://chromedriver.chromium.org/downloads")
                print(f"   (Cần version tương thích với Chrome {chrome_version})")
        else:
            print(f"❌ File ChromeDriver không tồn tại: {driver_path}")
            
    except ImportError:
        print("❌ webdriver-manager chưa được cài đặt")
        print("💡 Chạy: pip install webdriver-manager")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        print("\n💡 Thử:")
        print("1. pip install --upgrade webdriver-manager selenium")
        print("2. Xóa cache: xóa thư mục .wdm trong user home")
        print("3. Chạy lại script này")

if __name__ == "__main__":
    check_chromedriver()

