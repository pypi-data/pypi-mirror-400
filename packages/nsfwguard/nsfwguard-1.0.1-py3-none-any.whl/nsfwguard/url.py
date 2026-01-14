import requests
import tempfile
import os

from .image import scan_image
from .video import scan_video

# supported extensions
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp")
VIDEO_EXT = (".mp4", ".mkv", ".avi", ".mov")

def scan_url(url: str, timeout: int = 15):
    """
    Download a file from URL and scan it for NSFW content.
    """
    headers = {
        "User-Agent": "nsfwguard/1.0"
    }

    r = requests.get(url, stream=True, timeout=timeout, headers=headers)
    r.raise_for_status()

    # detect extension
    ext = os.path.splitext(url.split("?")[0])[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                tmp.write(chunk)
        path = tmp.name

    try:
        if ext in IMAGE_EXT:
            return {"type": "image", **scan_image(path)}
        elif ext in VIDEO_EXT:
            return {"type": "video", **scan_video(path)}
        else:
            return {
                "nsfw": False,
                "type": "unknown",
                "note": "unsupported file type"
            }
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
