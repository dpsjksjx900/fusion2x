import logging
import os
from datetime import datetime


def get_logger(log_file, module_name=None):
    """
    Returns a logger configured to write to the specified log_file.
    Adds a header with a timestamp at the top of the file if first use.
    """
    logger_name = f"fusion2x_{os.path.basename(log_file)}"
    logger = logging.getLogger(logger_name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        # Write header only if file is empty
        if os.stat(log_file).st_size == 0:
            start_line = (
                "=== Fusion2X"
                f"{' [' + module_name + ']' if module_name else ''}"
                f" Log Started: "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n"
            )
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(start_line)
    return logger
