import os
import subprocess
from utils.process_utils import require_binaries

def encode_video(frame_dir, output_path, fps=30, resolution=None, format="mp4", logger=None):
    """
    Encodes image frames in frame_dir into a video using ffmpeg.
    
    Args:
        frame_dir (str): Directory containing processed frames.
        output_path (str): Path for the output video file.
        fps (int): Target framerate.
        resolution (str): Optional, e.g., "1920x1080".
        format (str): Output video format, default mp4.
        logger: Logger instance.
    """
    require_binaries(["ffmpeg"])
    input_pattern = os.path.join(frame_dir, "frame_%06d.png")
    cmd = ["ffmpeg", "-framerate", str(fps), "-i", input_pattern]
    if resolution:
        cmd += ["-s", resolution]
    format = format.lower()
    if format == "gif":
        cmd += ["-y", output_path]
    else:
        cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-y", output_path]
    if logger:
        logger.info(f"[VideoEncoder] Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
