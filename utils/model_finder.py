import os


def find_model_executable(base_dir, model_name, exe_name=None, logger=None):
    """
    Searches for the given model's executable (.exe) in all subfolders and their subsubfolders of base_dir.
    Only searches two levels deep: subfolders and subsubfolders.

    Args:
        base_dir (str): The directory to search under (e.g., models/upscaling or models/interpolation)
        model_name (str): Name prefix for the model executable (e.g., 'waifu2x-ncnn-vulkan')
        exe_name (str, optional): Executable name to look for. Defaults to model_name + ".exe"
        logger (logging.Logger, optional): Logger to use for info/debug/errors

    Returns:
        str or None: Full path to the executable if found, else None
    """
    exe_name = exe_name or (model_name + ".exe")
    if not os.path.exists(base_dir):
        if logger:
            logger.error(f"Model root {base_dir} does not exist!")
        return None

    # Check all immediate subfolders
    for subfolder in os.listdir(base_dir):
        subfolder_path = os.path.join(base_dir, subfolder)
        if not os.path.isdir(subfolder_path):
            continue
        # Check in subfolder itself
        candidate = os.path.join(subfolder_path, exe_name)
        if os.path.isfile(candidate):
            if logger:
                logger.info(f"Found model exe: {candidate}")
            return candidate
        # Check in subsubfolders
        for subsubfolder in os.listdir(subfolder_path):
            subsubfolder_path = os.path.join(subfolder_path, subsubfolder)
            if not os.path.isdir(subsubfolder_path):
                continue
            candidate2 = os.path.join(subsubfolder_path, exe_name)
            if os.path.isfile(candidate2):
                if logger:
                    logger.info(f"Found model exe: {candidate2}")
                return candidate2
            if logger:
                logger.debug(f"Checked: {subsubfolder_path}")
        if logger:
            logger.debug(f"Checked: {subfolder_path}")
    if logger:
        logger.error(
            f"{exe_name} not found in any subfolder or subsubfolder of {base_dir}"
        )
    return None
