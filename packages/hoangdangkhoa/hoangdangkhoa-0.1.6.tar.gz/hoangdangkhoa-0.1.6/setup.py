from setuptools import setup, find_packages
import time
import sys

# Đoạn code này sẽ chạy ngay khi pip install
print("\n" + "="*50)
print("DANG KHOI TAO HE THONG HOANG DANG KHOA...")
print("="*50)

# Giả lập load nhiều dòng code/thông số
fake_logs = [
    "Checking dependencies...",
    "Fetching metadata from core server...",
    "Linking hoangdangkhoa-modules-v2.0...",
    "Optimizing bytecode for architecture x86_64...",
    "Injecting custom color protocols...",
    "Applying ANSI escape sequences...",
    "Setting up local environment variables...",
    "Finalizing security handshake..."
]

for log in fake_logs:
    print(f"  > {log}")
    time.sleep(0.3) # Tạo độ trễ để người dùng kịp nhìn thấy chữ chạy

print("="*50 + "\n")

setup(
    name="hoangdangkhoa",
    version="0.1.6", # Luôn nhớ tăng version mỗi lần upload
    packages=find_packages(),
    # Thêm nhiều thư viện phụ thuộc để pip hiện thêm các dòng "Collecting..."
    install_requires=[
        'numpy',
        'requests',
        'colorama',
        'pandas',
        'tqdm'
    ],
)