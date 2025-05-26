from handlers.models.rife_ncnn_vulkan import run_rife_ncnn_vulkan, supported_rife_ncnn_vulkan_params

# Central registry: key = model name, value = (runner function, supported_params)
MODEL_REGISTRY = {
    "rife-ncnn-vulkan": (run_rife_ncnn_vulkan, supported_rife_ncnn_vulkan_params),
    # Add more interpolation models here as needed.
}

def run_interpolation(frame_dir, interpolation_params, logger):
    """
    Runs the requested interpolation model on frames in frame_dir.
    Returns dict: {"success": bool, "message": str}
    """
    model_name = interpolation_params.get("model_name")
    params = interpolation_params.get("params", {})

    if model_name not in MODEL_REGISTRY:
        msg = f"Unknown interpolation model '{model_name}'"
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
        logger.info(f"Running interpolation model: {model_name}")
        model_func(frame_dir=frame_dir, params=params, logger=logger)
        return {"success": True, "message": "Interpolation completed."}
    except Exception as e:
        logger.error(f"Interpolation model '{model_name}' failed: {e}")
        return {"success": False, "message": str(e)}
