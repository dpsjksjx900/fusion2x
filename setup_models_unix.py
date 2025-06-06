import os
import sys
import requests
import shutil
import subprocess

# Logging setup
from utils.logger import get_logger

LOG_PATH = os.path.join("logs", "install_unix.log")
os.makedirs("logs", exist_ok=True)
logger = get_logger(LOG_PATH)

# Model release info
MODELS = [
    {
        "name": "rife-ncnn-vulkan",
        "repo": "nihui/rife-ncnn-vulkan",
        "asset_filter": lambda asset: asset["name"].endswith("ubuntu.zip"),
        "category": "interpolation",
    },
    {
        "name": "waifu2x-ncnn-vulkan",
        "repo": "nihui/waifu2x-ncnn-vulkan",
        "asset_filter": lambda asset: asset["name"].endswith("ubuntu.zip"),
        "category": "upscaling",
    },
    {
        "name": "realesrgan-ncnn-vulkan",
        "repo": "xinntao/Real-ESRGAN-ncnn-vulkan",
        "asset_filter": lambda asset: asset["name"].endswith("ubuntu.zip"),
        "category": "upscaling",
    },
    {
        "name": "realcugan-ncnn-vulkan",
        "repo": "nihui/realcugan-ncnn-vulkan",
        "asset_filter": lambda asset: asset["name"].endswith("ubuntu.zip"),
        "category": "upscaling",
    },
    {
        "name": "realsr-ncnn-vulkan",
        "repo": "nihui/realsr-ncnn-vulkan",
        "asset_filter": lambda asset: asset["name"].endswith("ubuntu.zip"),
        "category": "upscaling",
    },
    {
        "name": "srmd-ncnn-vulkan",
        "repo": "nihui/srmd-ncnn-vulkan",
        "asset_filter": lambda asset: asset["name"].endswith("ubuntu.zip"),
        "category": "upscaling",
    },
]

REQUIRED_TOOLS = ["wget", "unzip"]


def check_tools():
    missing = [t for t in REQUIRED_TOOLS if shutil.which(t) is None]
    if missing:
        logger.error(f"Missing required tools: {', '.join(missing)}")
        print(f"❌ Please install the following tools and rerun: {', '.join(missing)}")
        sys.exit(1)
    logger.info("All required tools are available.")


def run_cmd(cmd):
    logger.info(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        logger.error(result.stderr.decode("utf-8", errors="ignore"))
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")


def get_latest_asset(repo, asset_filter):
    api = f"https://api.github.com/repos/{repo}/releases/latest"
    resp = requests.get(api, timeout=30)
    if resp.status_code != 200:
        logger.error(f"Failed to fetch release for {repo}: HTTP {resp.status_code}")
        return None, None
    data = resp.json()
    for asset in data.get("assets", []):
        if asset_filter(asset):
            return asset["browser_download_url"], asset["name"]
    logger.error(f"No suitable asset found for {repo}")
    return None, None


def setup_model(model):
    cat_dir = os.path.join("models", model["category"])
    os.makedirs(cat_dir, exist_ok=True)
    print(f"\n==== Setting up {model['name']} ({model['category']}) ====")
    url, asset_name = get_latest_asset(model["repo"], model["asset_filter"])
    if not url:
        print("  ❌ Asset not found, skipping.")
        return
    version_folder = asset_name.replace(".zip", "")
    dest_dir = os.path.join(cat_dir, version_folder)
    if os.path.isdir(dest_dir):
        print(f"  ✅ {model['name']} already installed: {dest_dir}")
        return
    zip_path = os.path.join(cat_dir, f"{model['name']}.zip")
    run_cmd(["wget", "-O", zip_path, url])
    run_cmd(["unzip", "-o", zip_path, "-d", cat_dir])
    os.remove(zip_path)
    print(f"  🎉 {model['name']} ready in {dest_dir}")


def main():
    print("\n========== Fusion2X Unix Model Installer ==========")
    check_tools()
    for m in MODELS:
        setup_model(m)
    print("\n✅ All models installed under models/.")


if __name__ == "__main__":
    main()
