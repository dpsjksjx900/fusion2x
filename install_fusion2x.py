import sys
import subprocess
import shutil
import platform

REQUIREMENTS = [
    "tqdm",
    "jsonschema"
    +PyQt5
+ffmpeg-python
    # Add more as needed
]

def print_header():
    print("="*50)
    print("    Fusion2X Installation Script")
    print("="*50)

def check_python_version():
    print("[*] Checking Python version...")
    if sys.version_info < (3, 8):
        print("[-] Python 3.8+ is required. Please upgrade your Python.")
        sys.exit(1)
    print(f"[+] Python {sys.version_info.major}.{sys.version_info.minor} detected.")

def pip_install(packages):
    print("[*] Installing Python requirements...")
    for pkg in packages:
        print(f"    Installing: {pkg}")
        result = subprocess.run([sys.executable, "-m", "pip", "install", pkg])
        if result.returncode != 0:
            print(f"[-] Failed to install {pkg}. Please install it manually.")
    print("[+] Python requirements installed.")

def check_ffmpeg():
    print("[*] Checking for ffmpeg and ffprobe...")
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if ffmpeg and ffprobe:
        print(f"[+] ffmpeg found: {ffmpeg}")
        print(f"[+] ffprobe found: {ffprobe}")
    else:
        print("[-] ffmpeg or ffprobe not found in PATH!")
        print("    Please install ffmpeg and add it to your PATH:")
        print("    - Windows: https://ffmpeg.org/download.html")
        print("    - Linux: sudo apt install ffmpeg")
        print("    - macOS: brew install ffmpeg")
        input("    Press Enter to continue after installing ffmpeg...")

def print_model_binary_instructions():
    print("\n[*] IMPORTANT: External model binaries required!")
    print("    - waifu2x-caffe: https://github.com/lltcggie/waifu2x-caffe/releases")
    print("    - Real-ESRGAN-ncnn-vulkan: https://github.com/xinntao/Real-ESRGAN-ncnn-vulkan/releases")
    print("    - rife-ncnn-vulkan: https://github.com/nihui/rife-ncnn-vulkan/releases")
    print("    Download the required binaries and specify their paths in your Fusion2X config file.")
    print("    Or add them to your system PATH for easier usage.")

def main():
    print_header()
    check_python_version()
    pip_install(REQUIREMENTS)
    check_ffmpeg()
    print_model_binary_instructions()
    print("\n[!] Fusion2X installation complete. You can now run the program.")

if __name__ == "__main__":
    main()
