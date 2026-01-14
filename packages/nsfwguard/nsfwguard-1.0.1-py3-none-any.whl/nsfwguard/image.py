import torch
from nudenet import NudeClassifier

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
_classifier = NudeClassifier(device=DEVICE)

def scan_image(path: str, threshold: float = 0.6):
    result = _classifier.classify(path)
    score = result[path]["unsafe"]
    return {
        "nsfw": score >= threshold,
        "score": round(score, 3),
        "device": DEVICE
    }
