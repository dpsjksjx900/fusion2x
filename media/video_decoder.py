import os
import subprocess

def extract_frames(video_path, output_dir, output_format="png", logger=None):
    """
    Extracts frames from a video file into output_dir using ffmpeg.
    Returns metadata dict: frame_count, resolution, fps (if available).
    
    Args:
        video_path (str): Path to the input video or gif.
        output_dir (str): Directory to save the extracted frames.
        output_format (str): Output image format (default: png).
        logger: Logger instance.
    
    Returns:
        dict: Metadata with keys frame_count, resolution, fps.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    # ffmpeg command
    out_pattern = os.path.join(output_dir, f"frame_%06d.{output_format}")
    cmd = [
        "ffmpeg", "-i", video_path, "-vsync", "0", out_pattern, "-hide_banner", "-loglevel", "error"
    ]
    if logger:
        logger.info(f"[VideoDecoder] Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    # Count extracted frames and get metadata (simplified)
    frames = sorted([f for f in os.listdir(output_dir) if f.endswith(f".{output_format}")])
    frame_count = len(frames)
    # Optional: get FPS/resolution using ffprobe
    try:
        import json as js
        probe_cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate",
            "-of", "json", video_path
        ]
        result = subprocess.run(probe_cmd, stdout=subprocess.PIPE, check=True)
        probe = js.loads(result.stdout)
        stream = probe['streams'][0]
        width = stream['width']
        height = stream['height']
        res = f"{width}x{height}"
        # FPS calculation
        fps_str = stream['r_frame_rate']
        num, denom = [int(x) for x in fps_str.split('/')]
        fps = num / denom if denom != 0 else 30
    except Exception as e:
        res = "unknown"
        fps = 30
        if logger:
            logger.warning(f"[VideoDecoder] ffprobe failed: {e}")

    return {
        "frame_count": frame_count,
        "resolution": res,
        "fps": fps
    }
