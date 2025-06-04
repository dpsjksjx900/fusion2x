import argparse
import os
import sys
import json
from utils.logger import get_logger

"""
Fusion2X Receiver
-----------------
Entry point for Fusion2X. Handles user input from CLI or GUI, converts to standardized JSON format, 
sends the request to the core operator, and reports results/errors to the user.

Input:
    - From CLI: arguments specifying task, file paths, formats, model choices, and parameters.
    - From GUI: ideally, a pre-built JSON configuration file or string.

Output:
    - Prints user-friendly message to console or returns output to GUI layer.
    - Output includes:
        - Success status
        - Exported file path (video or image)
        - Log file path
        - Error code/message (if failed)
"""


def get_run_log_path():
    """Determine the path for the run log file."""
    env_path = os.environ.get("FUSION2X_LOG_PATH")
    if env_path:
        return env_path

    # fallback: generate a new log file path
    import datetime
    import random
    import string

    dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    rid = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    os.makedirs("logs", exist_ok=True)
    return os.path.join("logs", f"fusion2x_{dt}_{rid}.log")


# Set up logger ONCE, at module level, for whole script
log_path = get_run_log_path()
logger = get_logger(log_path, module_name="Receiver")


def parse_cli_args():
    """Parse CLI arguments for Fusion2X video/image processing."""
    parser = argparse.ArgumentParser(
        description="Fusion2X: AI Video Frame Interpolation and Upscaling Tool"
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to JSON config file (preferred for complex tasks)'
    )
    parser.add_argument(
        '--task',
        type=str,
        choices=['upscaling', 'interpolation', 'both'],
        help='Task to perform'
    )
    parser.add_argument('--input_path', type=str, help='Input file or directory')
    parser.add_argument(
        '--output_path',
        type=str,
        help='Export/output file or directory (optional)'
    )
    parser.add_argument(
        '--input_format',
        type=str,
        help='Input file format (e.g., mp4, png)'
    )
    parser.add_argument(
        '--output_format',
        type=str,
        help='Output file format (e.g., mp4, png)'
    )
    # (Add more argument options as needed for models/params...)

    args = parser.parse_args()
    return args


def build_json_from_args(args):
    """
    Build a standardized JSON request from CLI arguments.
    Only the most basic options shown—extend as needed!
    """
    request = {
        "task": args.task,
        "input_format": args.input_format,
        "output_format": args.output_format,
        "input_path": args.input_path,
        "output_path": args.output_path,
        # Additional options can be populated here as needed.
    }
    # Remove None fields (if args not supplied)
    request = {k: v for k, v in request.items() if v is not None}
    return request


def main():
    try:
        logger.info("Fusion2X receiver started.")

        # Read job request as JSON from stdin
        input_data = ""
        if not sys.stdin.isatty():
            input_data = sys.stdin.read()
            logger.info("Received JSON from stdin.")
        else:
            logger.error("No input received. Exiting.")
            print(json.dumps({"status": "error", "message": "No input provided.", "log_path": log_path}))
            sys.exit(1)

        try:
            json_request = json.loads(input_data)
        except Exception as e:
            logger.error(f"Failed to parse input JSON: {e}")
            print(json.dumps({"status": "error", "message": "Failed to parse input JSON.", "log_path": log_path}))
            sys.exit(1)

        logger.info(f"Received job config: {json.dumps(json_request, indent=2)}")

        # Add log_path to the request, if not already present
        if "log_path" not in json_request:
            json_request["log_path"] = log_path

        # Minimal input validation
        required = ["task", "input_path", "input_format", "output_format"]
        missing = [k for k in required if not json_request.get(k)]
        if missing:
            msg = f"Missing required fields: {missing}"
            logger.error(msg)
            print(json.dumps({"status": "error", "message": msg, "log_path": log_path}))
            sys.exit(1)

        # Optionally, check input and output files/dirs
        if not os.path.exists(json_request["input_path"]):
            msg = f"Input file does not exist: {json_request['input_path']}"
            logger.error(msg)
            print(json.dumps({"status": "error", "message": msg, "log_path": log_path}))
            sys.exit(1)
        if not json_request.get("output_path"):
            msg = "Output directory not specified."
            logger.error(msg)
            print(json.dumps({"status": "error", "message": msg, "log_path": log_path}))
            sys.exit(1)

        # Import operator only when ready to process (avoid import-time side effects)
        from core.operator import process_request

        # Pass log_path to operator via json_request
        result = process_request(json_request)

        # Always attach log_path to the result
        result["log_path"] = log_path

        logger.info(f"Job result: {result}")
        print(json.dumps(result))
    except Exception as e:
        logger.error(f"Exception occurred: {e}", exc_info=True)
        print(json.dumps({
            "status": "error",
            "message": f"Exception occurred: {e}",
            "log_path": log_path
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
