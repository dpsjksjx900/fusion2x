import sys
import subprocess
import shutil
import platform
import os

from utils import env_setup

REQUIREMENTS = [
    "tqdm",
    "jsonschema",
]


def load_requirements():
    """Return a list of required packages."""
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines()]
        return [l for l in lines if l and not l.startswith("#")]
    return REQUIREMENTS

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


def install_win_runtime():
    """Ensure the Microsoft Visual C++ runtime is installed on Windows."""
    if platform.system().lower() != "windows":
        return
    print("[*] Checking for Visual C++ runtime...")
    if env_setup.vc_runtime_installed():
        print("[+] Visual C++ runtime detected.")
        return

    print("[!] Visual C++ runtime missing. Installing...")
    try:
        success = env_setup.install_vc_runtime()
        if success:
            print("[+] Visual C++ runtime installed.")
        else:
            print("[-] Failed to verify Visual C++ runtime installation.")
    except Exception as exc:
        print(f"[-] Failed to install Visual C++ runtime: {exc}")

def main():
    print_header()
    check_python_version()
    install_win_runtime()
    pip_install(load_requirements())
    check_ffmpeg()
    print_model_binary_instructions()
    print("\n[!] Fusion2X installation complete. You can now run the program.")

if __name__ == "__main__":
    main()
