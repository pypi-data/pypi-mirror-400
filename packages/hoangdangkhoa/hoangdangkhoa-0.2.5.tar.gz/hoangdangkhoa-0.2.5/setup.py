from setuptools import setup, find_packages
import time
import sys

# --- PHẦN LÀM CHO NGẦU (CHẠY KHI PIP INSTALL) ---
print("\n" + "="*60)
print("\033[1;36mKHOI CHAY HE THONG CAI DAT HOANG DANG KHOA v0.2.5\033[0m")
print("="*60)

logs = [
    "[INFO] Connecting to Hoang Dang Khoa's private server...",
    "[INFO] Verifying security tokens...",
    "[DEBUG] Analyzing local environment architecture: x86_64",
    "[DEBUG] Loading ANSI color protocols...",
    "[PROCESS] Injecting core modules to site-packages...",
    "[WARNING] High performance computing mode enabled.",
    "[SUCCESS] Secure connection established."
]

for log in logs:
    print(f"  > {log}")
    time.sleep(0.4) # Tạo độ trễ để người dùng nhìn thấy từng dòng chạy

# Hiệu ứng thanh load giả
for i in range(1, 21):
    sys.stdout.write(f"\r\033[32mFinalizing: [{'#' * i}{'.' * (20 - i)}] {i*5}%\033[0m")
    sys.stdout.flush()
    time.sleep(0.1)
print("\n" + "="*60 + "\n")
# -----------------------------------------------

setup(
    name="hoangdangkhoa",
    version="0.2.5", # Tăng version lên bản mới nhất
    packages=find_packages(),
    # Danh sách các thư viện nặng nhất để pip hiện "Collecting..." thật dài
    install_requires=[
        'torch',        # Cực nặng (vài trăm MB)
        'tensorflow',   # Siêu nặng
        'pandas',
        'scipy',
        'matplotlib',
        'scikit-learn'
    ],
)