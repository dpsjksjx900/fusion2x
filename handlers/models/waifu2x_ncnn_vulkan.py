import os
import subprocess
from utils.model_finder import find_model_executable

supported_waifu2x_ncnn_vulkan_params = [
    "waifu2x_exe_path",   # Path to waifu2x-ncnn-vulkan.exe (optional if using default)
    "scale",              # Scale factor (1, 2, 4, etc.)
    "noise_level",        # Denoise level (0, 1, 2, 3)
    "mode",               # 'noise', 'scale', or 'noise_scale'
    "model_dir",          # Model directory to use (e.g., models-upconv_7_photo, optional)
    "output_format",      # Output format: png, jpg, etc.
    "gpu_id",             # GPU selection (integer, optional)
    "threads",            # Thread count (optional)
    "tile_size",          # Tile size (optional)
]

def find_default_waifu2x_exe():
    """
    Attempts to find the latest waifu2x-ncnn-vulkan.exe in models/upscaling/
    """
    model_base = os.path.abspath(
        os.path.join(
        os.path.dirname(__file__),
        "..", "..",    # ↑ too many “..”
        "models", "upscaling"
        )
    )
    if not os.path.exists(model_base):
        return None
    candidates = [f for f in os.listdir(model_base) if f.startswith("waifu2x-ncnn-vulkan") and os.path.isdir(os.path.join(model_base, f))]
    if not candidates:
        return None
    candidates.sort(reverse=True)
    exe = os.path.join(model_base, candidates[0], "waifu2x-ncnn-vulkan.exe")
    return exe if os.path.isfile(exe) else None

def run_waifu2x_ncnn_vulkan(frame_dir, params, logger):
    exe_path = params.get("waifu2x_exe_path")
    if not exe_path:
        model_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "upscaling")
        )
        exe_path = find_model_executable(model_root, "waifu2x-ncnn-vulkan", logger=logger)
    if not exe_path or not os.path.isfile(exe_path):
        logger.error(f"waifu2x-ncnn-vulkan.exe not found! Searched for: {exe_path}")
        raise FileNotFoundError("waifu2x-ncnn-vulkan.exe not found in models/upscaling/.")

    scale = params.get("scale", 2)
    noise_level = params.get("noise_level", 2)
    mode = params.get("mode", "noise_scale")
    model_dir = params.get("model_dir")  # e.g., "models-upconv_7_photo"
    output_format = params.get("output_format", "png")
    gpu_id = params.get("gpu_id", 0)
    threads = params.get("threads", 2)
    tile_size = params.get("tile_size", 0)  # 0 = auto

    # If model_dir is not given, use a default inside the waifu2x folder
    if not model_dir:
        waifu2x_folder = os.path.dirname(exe_path)
        model_dir = os.path.join(waifu2x_folder, "models-upconv_7_photo")

    output_dir = frame_dir  # In-place for now

    cmd = [
        exe_path,
        "-i", frame_dir,
        "-o", output_dir,
        "-n", str(noise_level),
        "-s", str(scale),
        "-m", mode,
        "-f", output_format,
        "-t", str(gpu_id),
        "-j", str(threads),
        "-x", model_dir
    ]
    if tile_size:
        cmd.extend(["-T", str(tile_size)])

    logger.info(f"[waifu2x-ncnn-vulkan] Running: {' '.join(str(x) for x in cmd)}")
    subprocess.run(cmd, check=True)
    logger.info(f"[waifu2x-ncnn-vulkan] Finished upscaling.")

