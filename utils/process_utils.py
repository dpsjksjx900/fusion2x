import subprocess


def run_model_command(cmd, logger):
    """Run an external model command with logging and rich error messages."""
    logger.info("[subprocess] Running: %s" % " ".join(str(x) for x in cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return

    logger.error(f"Model process failed with code {result.returncode}")
    if result.stdout:
        logger.error(result.stdout)
    if result.stderr:
        logger.error(result.stderr)

    # Provide a helpful message for common crash code 3221225477 (0xC0000005)
    if result.returncode in (3221225477, -1073741819):
        hint = (
            "The process crashed (0xC0000005). This often indicates missing or "
            "incompatible GPU drivers or Visual C++ runtime components."
        )
    else:
        hint = f"Model process returned exit code {result.returncode}."
    raise RuntimeError(hint)
