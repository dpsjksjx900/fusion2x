import os
import subprocess
from utils.model_finder import find_model_executable
from utils.process_utils import run_model_command


supported_realesrgan_ncnn_vulkan_params = [
    "realesrgan_exe_path",  # Path to realesrgan-ncnn-vulkan.exe (optional)
    "scale",                # Scale factor (e.g., 2, 4)
    "model",                # Model name (e.g., realesrgan-x4plus, realesr-animevideov3)
    "output_format",        # Output format: png, jpg, etc.
    "gpu_id",               # GPU selection (integer, optional)
    "tile_size",            # Tile size (optional)
    "threads",              # Thread count (optional)
]

def find_default_realesrgan_exe():
    """
    Find the latest realesrgan-ncnn-vulkan.exe in models/upscaling/
    """
    model_base = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "models", "upscaling")
    )
    if not os.path.exists(model_base):
        return None
    candidates = [f for f in os.listdir(model_base) if f.startswith("realesrgan-ncnn-vulkan") and os.path.isdir(os.path.join(model_base, f))]
    if not candidates:
        return None
    candidates.sort(reverse=True)
    exe = os.path.join(model_base, candidates[0], "realesrgan-ncnn-vulkan.exe")
    return exe if os.path.isfile(exe) else None

def run_realesrgan_ncnn_vulkan(frame_dir, params, logger):
    exe_path = params.get("realesrgan_exe_path")
    if not exe_path:
        model_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "models", "upscaling")
        )
        exe_path = find_model_executable(model_root, "realesrgan-ncnn-vulkan", logger=logger)
    if not exe_path or not os.path.isfile(exe_path):
        logger.error(f"realesrgan-ncnn-vulkan.exe not found! Searched for: {exe_path}")
        raise FileNotFoundError("realesrgan-ncnn-vulkan.exe not found in models/upscaling/.")

    scale = params.get("scale", 2)
    model = params.get("model", "realesrgan-x4plus")
    output_format = params.get("output_format", "png")
    gpu_id = params.get("gpu_id", 0)
    tile_size = params.get("tile_size", 0)  # 0 = auto
    threads = params.get("threads", 2)

    output_dir = frame_dir  # In-place for now

    cmd = [
        exe_path,
        "-i", frame_dir,
        "-o", output_dir,
        "-n", model,
        "-s", str(scale),
        "-f", output_format,
        "-g", str(gpu_id),
        "-j", str(threads)
    ]
    if tile_size:
        cmd.extend(["-t", str(tile_size)])

    run_model_command(cmd, logger)
    logger.info(f"[realesrgan-ncnn-vulkan] Finished upscaling.")
