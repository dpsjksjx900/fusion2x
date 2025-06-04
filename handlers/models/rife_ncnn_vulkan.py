import os
import subprocess
from utils.model_finder import find_model_executable

supported_rife_ncnn_vulkan_params = [
    "rife_exe_path",     # Path to rife-ncnn-vulkan.exe (optional if using default)
    "model",             # Model version/folder, e.g. rife-v4.6
    "times",             # Interpolation multiplier (2=double, 4=quadruple)
    "output_format",     # Output image format: png, jpg, etc.
    "gpu_id",            # GPU selection (integer)
    "threads",           # Number of threads
    "tta_mode",          # Enable TTA mode (True/False)
    "uhd_mode",          # Enable UHD mode (True/False)
    "input_format"       # Input image format (optional)
]

def find_default_rife_exe():
    """
    Attempts to find the latest rife-ncnn-vulkan.exe in models/interpolation/
    """
    model_base = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "models", "interpolation")
    )
    # Find the folder starting with 'rife-ncnn-vulkan'
    if not os.path.exists(model_base):
        return None
    candidates = [f for f in os.listdir(model_base) if f.startswith("rife-ncnn-vulkan") and os.path.isdir(os.path.join(model_base, f))]
    if not candidates:
        return None
    # If multiple, pick the last in lexicographic order (should be latest)
    candidates.sort(reverse=True)
    exe = os.path.join(model_base, candidates[0], "rife-ncnn-vulkan.exe")
    return exe if os.path.isfile(exe) else None

def run_rife_ncnn_vulkan(frame_dir, params, logger):
    exe_path = params.get("rife_exe_path")
    if not exe_path:
        model_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "models", "interpolation")
        )
        exe_path = find_model_executable(model_root, "rife-ncnn-vulkan", logger=logger)
    if not exe_path or not os.path.isfile(exe_path):
        logger.error(f"rife-ncnn-vulkan.exe not found! Searched for: {exe_path}")
        raise FileNotFoundError("rife-ncnn-vulkan.exe not found in models/interpolation/.")
    
    model = params.get("model", "rife-v4.6")
    times = params.get("times", 2)
    fmt = params.get("output_format", "png")
    gpu_id = params.get("gpu_id", 0)
    threads = params.get("threads", 4)
    tta_mode = params.get("tta_mode", False)
    uhd_mode = params.get("uhd_mode", False)
    input_format = params.get("input_format", "png")

    output_dir = frame_dir

    cmd = [
        exe_path,
        "-i",
        frame_dir,
        "-o",
        output_dir,
        "-n",
        str(times),
        "-m",
        model,
        "-f",
        fmt,
        "-j",
        str(threads),
        "-g",
        str(gpu_id),
    ]
    if tta_mode:
        cmd.append("-x")
    if uhd_mode:
        cmd.append("--uhd")

    logger.info(f"[rife-ncnn-vulkan] Running: {' '.join(str(x) for x in cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Model process failed with code {result.returncode}")
        logger.error(result.stdout)
        logger.error(result.stderr)
        result.check_returncode()
    logger.info(f"[rife-ncnn-vulkan] Finished interpolation.")

