import cv2
import tempfile
from .image import scan_image

def scan_video(path: str, frame_gap=30, nsfw_ratio=0.2):
    cap = cv2.VideoCapture(path)
    total, flagged = 0, 0

    with tempfile.TemporaryDirectory() as tmp:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            total += 1
            if total % frame_gap != 0:
                continue

            frame_path = f"{tmp}/{total}.jpg"
            cv2.imwrite(frame_path, frame)

            if scan_image(frame_path)["nsfw"]:
                flagged += 1

    cap.release()
    ratio = flagged / max(total, 1)

    return {
        "nsfw": ratio >= nsfw_ratio,
        "ratio": round(ratio, 3)
    }
