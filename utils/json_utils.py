import json

def load_json_from_file(json_file):
    """
    Loads and parses a JSON file. Returns the loaded dict.
    """
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_json_request(request):
    """
    Validates a Fusion2X job JSON request.
    Returns (True, "") if valid, (False, reason) if not.
    """
    required_fields = ["task", "input_format", "output_format", "input_path"]
    for field in required_fields:
        if field not in request:
            return False, f"Missing required field '{field}'"
    # Additional checks for mutually required blocks
    task = request.get("task")
    if task == "upscaling" and "upscaling" not in request:
        return False, "Task is 'upscaling' but no 'upscaling' block found."
    if task == "interpolation" and "interpolation" not in request:
        return False, "Task is 'interpolation' but no 'interpolation' block found."
    if task == "both" and ("upscaling" not in request or "interpolation" not in request):
        return False, "Task is 'both' but required blocks are missing."
    # All checks passed
    return True, ""
