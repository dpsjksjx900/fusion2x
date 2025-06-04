def build_result_signal(
    status, output_path=None, log_path=None, message="", extra=None
):
    """
    Builds a result signal dictionary.
    """
    signal = {
        "status": status,        # "success" or "error"
        "output_path": output_path,
        "log_path": log_path,
        "message": message
    }
    if extra:
        signal.update(extra)
    return signal
