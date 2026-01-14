from .image import scan_image
from .video import scan_video

def scan_batch(paths: list):
    results = []
    for p in paths:
        if p.lower().endswith((".jpg", ".png", ".jpeg")):
            results.append({"file": p, **scan_image(p)})
        elif p.lower().endswith((".mp4", ".mkv", ".avi")):
            results.append({"file": p, **scan_video(p)})
    return results
