import os
import sys
import requests
import zipfile
import shutil
import urllib.request
import platform
import subprocess


# ---- Setup Logging ----
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "utils")))
from utils.logger import get_logger

LOG_PATH = os.path.join("logs", "install.log")
os.makedirs("logs", exist_ok=True)
logger = get_logger(LOG_PATH)

# ---- Model Download Info ----
MODELS = [
    {
        "name": "rife-ncnn-vulkan",
        "repo": "nihui/rife-ncnn-vulkan",
        "asset_filter": lambda asset: asset["name"].endswith("windows.zip"),
        "category": "interpolation"
    },
    {
        "name": "waifu2x-ncnn-vulkan",
        "repo": "nihui/waifu2x-ncnn-vulkan",
        "asset_filter": lambda asset: asset["name"].endswith("windows.zip"),
        "category": "upscaling"
    },
    {
        "name": "realesrgan-ncnn-vulkan",
        "repo": "xinntao/Real-ESRGAN-ncnn-vulkan",
        "asset_filter": lambda asset: asset["name"].endswith("windows.zip"),
        "category": "upscaling"
    },
    {
        "name": "realcugan-ncnn-vulkan",
        "repo": "nihui/realcugan-ncnn-vulkan",
        "asset_filter": lambda asset: asset["name"].endswith("windows.zip"),
        "category": "upscaling"
    },
    {
        "name": "realsr-ncnn-vulkan",
        "repo": "nihui/realsr-ncnn-vulkan",
        "asset_filter": lambda asset: asset["name"].endswith("windows.zip"),
        "category": "upscaling"
    },
    {
        "name": "srmd-ncnn-vulkan",
        "repo": "nihui/srmd-ncnn-vulkan",
        "asset_filter": lambda asset: asset["name"].endswith("windows.zip"),
        "category": "upscaling"
    }
]

FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_FOLDER = "ffmpeg"

def is_windows():
    result = platform.system().lower() == "windows"
    logger.info(f"Detected OS: {platform.system()} (is_windows={result})")
    return result

def download_file(url, out_path):
    try:
        logger.info(f"Downloading from: {url}")
        print(f"  ➡️ Downloading from: {url}")
        urllib.request.urlretrieve(url, out_path)
        logger.info(f"Downloaded to: {out_path}")
        print(f"  ✅ Downloaded to: {out_path}")
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        print(f"  ❌ Failed to download {url}: {e}")

def extract_zip(zip_path, extract_to):
    try:
        logger.info(f"Extracting {zip_path} to {extract_to} ...")
        print(f"  ➡️ Extracting {zip_path} to {extract_to} ...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)
        logger.info("Extraction complete.")
        print(f"  ✅ Extracted.")
    except Exception as e:
        logger.error(f"Failed to extract {zip_path}: {e}")
        print(f"  ❌ Failed to extract {zip_path}: {e}")

def clean_folder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)
    logger.info(f"Prepared clean folder: {folder}")

def get_latest_release_asset_url(repo, asset_filter):
    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        resp = requests.get(api_url)
        if resp.status_code != 200:
            logger.error(f"Could not fetch release for {repo}: HTTP {resp.status_code}")
            print(f"  ❌ Could not fetch release for {repo}!")
            return None, None
        data = resp.json()
        for asset in data.get("assets", []):
            if asset_filter(asset):
                logger.info(f"Found asset for {repo}: {asset['name']}")
                return asset["browser_download_url"], asset["name"]
        logger.error(f"Could not find the required asset in {repo} latest release.")
        print(f"  ❌ Could not find the required asset in {repo} latest release.")
        return None, None
    except Exception as e:
        logger.error(f"Failed to query {repo} releases: {e}")
        print(f"  ❌ Failed to query {repo}: {e}")
        return None, None

def setup_model(model):
    category_folder = os.path.join("models", model["category"])
    os.makedirs(category_folder, exist_ok=True)
    print(f"\n==== Setting up {model['name']} ({model['category']}) ====")
    logger.info(f"Setting up {model['name']} in {category_folder}")
    url, asset_name = get_latest_release_asset_url(model["repo"], model["asset_filter"])
    if not url:
        logger.warning(f"Skipping {model['name']} (URL not found).")
        print(f"  ❌ Skipping {model['name']} (URL not found).")
        return
    # Determine versioned folder name from the asset zip filename (strip .zip)
    versioned_folder_name = asset_name.replace(".zip", "")
    versioned_folder_path = os.path.join(category_folder, versioned_folder_name)
    exe_name = f"{model['name']}.exe"
    exe_path = os.path.join(versioned_folder_path, exe_name)
    if os.path.exists(versioned_folder_path) and os.path.isfile(exe_path):
        logger.info(f"{model['name']} already exists at {versioned_folder_path}, skipping download.")
        print(f"  ✅ {model['name']} already installed: {versioned_folder_path}")
        return
    zip_name = f"{model['name']}.zip"
    download_file(url, zip_name)
    extract_zip(zip_name, category_folder)
    os.remove(zip_name)
    logger.info(f"{model['name']} setup complete in {category_folder}/[version-folder]/")
    print(f"  🎉 {model['name']} is ready in {category_folder}/[version-folder]/")

def check_ffmpeg():
    from shutil import which
    found = which("ffmpeg") is not None
    logger.info(f"FFmpeg found in PATH: {found}")
    return found

def setup_ffmpeg():
    print(f"\n==== Setting up FFmpeg ====")
    logger.info("Setting up FFmpeg.")
    if check_ffmpeg():
        print("  ✅ FFmpeg already in PATH.")
        logger.info("FFmpeg already in PATH, skipping download.")
        return
    if os.path.exists(FFMPEG_FOLDER):
        shutil.rmtree(FFMPEG_FOLDER)
    os.makedirs(FFMPEG_FOLDER, exist_ok=True)
    zip_name = "ffmpeg.zip"
    download_file(FFMPEG_URL, zip_name)
    extract_zip(zip_name, FFMPEG_FOLDER)
    os.remove(zip_name)
    # Move the extracted files up if needed
    entries = os.listdir(FFMPEG_FOLDER)
    for entry in entries:
        full_entry = os.path.join(FFMPEG_FOLDER, entry)
        if os.path.isdir(full_entry) and entry.lower().startswith("ffmpeg"):
            for sub in os.listdir(full_entry):
                shutil.move(os.path.join(full_entry, sub), os.path.join(FFMPEG_FOLDER, sub))
            shutil.rmtree(full_entry)
    logger.info("FFmpeg setup complete.")
    print(f"  🎉 FFmpeg is ready in {FFMPEG_FOLDER}/bin/")

def pip_install_requirements():
    logger.info("Installing Python requirements from requirements.txt...")
    print("\n==== Installing Python requirements ====")
    cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
    result = subprocess.run(cmd)
    if result.returncode == 0:
        logger.info("Python requirements installed successfully.")
        print("  ✅ Python requirements installed.")
    else:
        logger.error("Failed to install Python requirements.")
        print("  ❌ Failed to install Python requirements.")


def main():
    print("\n========== Fusion2X Model Auto-Installer ==========")
    logger.info("=== Starting Fusion2X Model Auto-Installer ===")
    if not is_windows():
        logger.error("This script is for Windows only. Aborting.")
        print("❌ This script is for Windows only. Please install models manually on other OSes.")
        sys.exit(1)
    pip_install_requirements()
    for model in MODELS:
        setup_model(model)
    setup_ffmpeg()
    logger.info("All model and FFmpeg installations completed.")
    print("\n✅ All done! All models are in models/[interpolation|upscaling]/. "
          "Make sure your handlers use the correct paths.")


if __name__ == "__main__":
    main()
