import os
import shutil
import traceback
from datetime import datetime

from media.video_decoder import extract_frames
from media.video_encoder import encode_video
from media.image_handler import process_image
from handlers.upscaling_handler import run_upscaling
from handlers.interpolation_handler import run_interpolation
from utils.logger import get_logger
from utils.file_utils import create_temp_folder, safe_rename, move_file

"""
Fusion2X Operator
-----------------
Main pipeline controller for Fusion2X. Receives a validated JSON request from
the receiver, coordinates temp folder setup, orchestrates decoding, upscaling,
interpolation, and encoding, handles all error signaling, and returns a
status/result object.

Input: JSON request object (dict)
Output: JSON result dict (status, output_path, log_path, message, etc.)
"""


def get_run_log_path():
    """Determine the path for the operator log file."""
    env_path = os.environ.get("FUSION2X_LOG_PATH")
    if env_path:
        return env_path

    import datetime
    import random
    import string

    dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    rid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    os.makedirs("logs", exist_ok=True)
    return os.path.join("logs", f"fusion2x_{dt}_{rid}.log")


log_path = get_run_log_path()
logger = get_logger(log_path, module_name="Operator")


def find_model_executable(model_root, model_name, exe_name=None):
    """
    Searches for the model executable in subfolders of model_root whose names start with model_name.
    Returns the full path to the executable or None if not found.
    """
    exe_name = exe_name or (model_name + '.exe')
    for subfolder in os.listdir(model_root):
        if subfolder.lower().startswith(model_name.lower()):
            candidate = os.path.join(model_root, subfolder, exe_name)
            if os.path.isfile(candidate):
                return candidate
    return None


def process_request(json_request):
    """
    Main entry point for processing a Fusion2X job.

    Args:
        json_request (dict): The JSON job request from receiver/GUI.

    Returns:
        dict: Result dict with at least keys: status, message, log_path, output_path.
    """
    try:
        original_file = os.path.abspath(json_request["input_path"])
        file_dir, file_name = os.path.split(original_file)
        file_base, file_ext = os.path.splitext(file_name)
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_folder = create_temp_folder(base_dir=file_dir, base_name=file_base, timestamp=now_str)
        os.makedirs("logs", exist_ok=True)

        # Use unified log_path if provided, else create a new one (should always be present)
        log_path = json_request.get("log_path", f"logs/process_{now_str}.log")
        logger = get_logger(log_path, module_name="Operator")

        result = {
            "status": "error",
            "log_path": log_path,
            "message": "",
            "output_path": None
        }

        logger.info(f"Started Fusion2X operator for file: {original_file}")
        logger.info(f"Job config: {json_request}")

        # Video processing
        if json_request["input_format"].lower() in ("mp4", "avi", "mov", "mkv", "gif"):
            logger.info("Detected video or gif input. Beginning frame extraction.")
            frames_dir = os.path.join(temp_folder, "frames")
            metadata = extract_frames(original_file, frames_dir, output_format="png", logger=logger)
            logger.info(f"Extracted frames. Metadata: {metadata}")

            # Perform upscaling first if needed
            if json_request["task"] in ("upscaling", "both") and json_request.get("upscaling", {}).get("enabled", False):
                logger.info("Starting upscaling process.")
                upscaling_result = run_upscaling(frames_dir, json_request["upscaling"], logger)
                if not upscaling_result.get("success"):
                    msg = upscaling_result.get("message", "Upscaling failed.")
                    logger.error(msg)
                    result["message"] = msg
                    return result
                logger.info("Upscaling complete.")

            # Interpolation if requested
            if json_request["task"] in ("interpolation", "both") and json_request.get("interpolation", {}).get("enabled", False):
                logger.info("Starting interpolation process.")
                interpolation_result = run_interpolation(frames_dir, json_request["interpolation"], logger)
                if not interpolation_result.get("success"):
                    msg = interpolation_result.get("message", "Interpolation failed.")
                    logger.error(msg)
                    result["message"] = msg
                    return result
                logger.info("Interpolation complete.")

            # Encode frames back to video
            logger.info("Starting video encoding.")
            target_fps = metadata.get("fps", 30)
            target_res = metadata.get("resolution", None)
            output_ext = "." + json_request.get("output_format", "mp4").lstrip(".")
            out_video_path = os.path.join(temp_folder, f"{file_base}_fusion2x_{now_str}{output_ext}")
            encode_video(frames_dir, out_video_path, fps=target_fps, resolution=target_res, logger=logger)
            logger.info(f"Video encoding complete: {out_video_path}")

            # Move result to output directory
            export_dir = json_request.get("output_path") or file_dir
            os.makedirs(export_dir, exist_ok=True)
            final_name = f"{file_base}_fusion2x_{now_str}{output_ext}"
            # Move the encoded video to the export directory and capture its new location
            moved_path = move_file(out_video_path, export_dir)
            # Rename to the final desired name
            final_path = safe_rename(moved_path, final_name)
            logger.info(f"Moved processed video to: {final_path}")

            # Cleanup
            try:
                shutil.rmtree(temp_folder)
                logger.info(f"Deleted temp folder: {temp_folder}")
            except Exception as e:
                logger.warning(f"Could not delete temp folder: {e}")

            result["status"] = "success"
            result["message"] = "Video processing complete."
            result["output_path"] = final_path
            return result

        # Image processing
        elif json_request["input_format"].lower() in ("png", "jpg", "jpeg", "webp"):
            logger.info("Detected image input. Beginning processing.")
            # Copy input image to temp folder
            img_temp = os.path.join(temp_folder, file_name)
            shutil.copy2(original_file, img_temp)
            frames_dir = temp_folder

            # Upscaling
            if json_request["task"] in ("upscaling", "both") and json_request.get("upscaling", {}).get("enabled", False):
                logger.info("Starting upscaling process.")
                upscaling_result = run_upscaling(frames_dir, json_request["upscaling"], logger)
                if not upscaling_result.get("success"):
                    msg = upscaling_result.get("message", "Upscaling failed.")
                    logger.error(msg)
                    result["message"] = msg
                    return result
                logger.info("Upscaling complete.")

            # Interpolation for image: usually not applicable, can log warning if needed

            # Move final image to export dir
            export_dir = json_request.get("output_path") or file_dir
            os.makedirs(export_dir, exist_ok=True)
            output_ext = "." + json_request.get("output_format", file_ext.lstrip(".")).lstrip(".")
            final_name = f"{file_base}_fusion2x_{now_str}{output_ext}"
            final_path = os.path.join(export_dir, final_name)
            process_image(frames_dir, final_path, logger=logger)
            logger.info(f"Moved processed image to: {final_path}")

            # Cleanup
            try:
                shutil.rmtree(temp_folder)
                logger.info(f"Deleted temp folder: {temp_folder}")
            except Exception as e:
                logger.warning(f"Could not delete temp folder: {e}")

            result["status"] = "success"
            result["message"] = "Image processing complete."
            result["output_path"] = final_path
            return result

        else:
            msg = f"Unsupported input format: {json_request['input_format']}"
            logger.error(msg)
            result["message"] = msg
            return result

    except Exception as e:
        msg = f"Exception occurred: {e}\n{traceback.format_exc()}"
        logger.error(msg)
        return {
            "status": "error",
            "log_path": log_path,
            "message": msg,
            "output_path": None
        }
