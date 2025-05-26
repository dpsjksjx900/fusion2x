from handlers.models.waifu2x_ncnn_vulkan import run_waifu2x_ncnn_vulkan, supported_waifu2x_ncnn_vulkan_params
from handlers.models.realesrgan_ncnn_vulkan import run_realesrgan_ncnn_vulkan, supported_realesrgan_ncnn_vulkan_params
from handlers.models.realcugan_ncnn_vulkan import run_realcugan_ncnn_vulkan, supported_realcugan_ncnn_vulkan_params
from handlers.models.realsr_ncnn_vulkan import run_realsr_ncnn_vulkan, supported_realsr_ncnn_vulkan_params
from handlers.models.srmd_ncnn_vulkan import run_srmd_ncnn_vulkan, supported_srmd_ncnn_vulkan_params

# Central registry: key = model name, value = (runner function, supported_params)
MODEL_REGISTRY = {
    "waifu2x-ncnn-vulkan": (run_waifu2x_ncnn_vulkan, supported_waifu2x_ncnn_vulkan_params),
    "realesrgan-ncnn-vulkan": (run_realesrgan_ncnn_vulkan, supported_realesrgan_ncnn_vulkan_params),
    "realcugan-ncnn-vulkan": (run_realcugan_ncnn_vulkan, supported_realcugan_ncnn_vulkan_params),
    "realsr-ncnn-vulkan": (run_realsr_ncnn_vulkan, supported_realsr_ncnn_vulkan_params),
    "srmd-ncnn-vulkan": (run_srmd_ncnn_vulkan, supported_srmd_ncnn_vulkan_params),
}

def run_upscaling(frame_dir, upscaling_params, logger):
    """
    Runs the requested upscaling model on frames in frame_dir.
    Returns dict: {"success": bool, "message": str}
    """
    model_name = upscaling_params.get("model_name")
    params = upscaling_params.get("params", {})

    if model_name not in MODEL_REGISTRY:
        msg = f"Unknown upscaling model '{model_name}'"
        logger.error(msg)
        return {"success": False, "message": msg}

    model_func, supported_params = MODEL_REGISTRY[model_name]
    # Parameter validation
    for k in params:
        if k not in supported_params:
            msg = f"Parameter '{k}' is not supported by model '{model_name}'"
            logger.error(msg)
            return {"success": False, "message": msg}

    try:
        logger.info(f"Running upscaling model: {model_name}")
        model_func(frame_dir=frame_dir, params=params, logger=logger)
        return {"success": True, "message": "Upscaling completed."}
    except Exception as e:
        logger.error(f"Upscaling model '{model_name}' failed: {e}")
        return {"success": False, "message": str(e)}
