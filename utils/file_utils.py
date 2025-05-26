import os
import shutil
import uuid

def create_temp_folder(base_dir, base_name, timestamp):
    """
    Create a temporary folder for processing.
    Folder name includes the original file's base name and a timestamp for uniqueness.
    Returns the path to the temp folder.
    """
    temp_folder = os.path.join(
        base_dir,
        f"{base_name}_fusion2x_temp_{timestamp}_{uuid.uuid4().hex[:6]}"
    )
    os.makedirs(temp_folder, exist_ok=True)
    return temp_folder

def move_file(src_path, dst_dir):
    """
    Move a file from src_path to dst_dir. Returns the new full path.
    Overwrites if the destination file exists.
    """
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok=True)
    file_name = os.path.basename(src_path)
    dst_path = os.path.join(dst_dir, file_name)
    shutil.move(src_path, dst_path)
    return dst_path

def safe_rename(src_path, new_name):
    """
    Rename a file safely within the same directory. Returns the new full path.
    """
    dir_path = os.path.dirname(src_path)
    dst_path = os.path.join(dir_path, new_name)
    os.rename(src_path, dst_path)
    return dst_path
