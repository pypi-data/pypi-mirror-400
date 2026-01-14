import argparse
from nsfwguard.image import scan_image
from nsfwguard.video import scan_video

def main():
    parser = argparse.ArgumentParser("nsfwguard-scan")
    parser.add_argument("file")
    args = parser.parse_args()

    if args.file.lower().endswith((".jpg", ".png", ".jpeg")):
        print(scan_image(args.file))
    else:
        print(scan_video(args.file))
