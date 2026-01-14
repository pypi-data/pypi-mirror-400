# nsfwguard



🚨 **GPU-accelerated NSFW content detection** for **images, videos, and URLs**.

`nsfwguard` is a Python tool designed for developers who need fast and reliable NSFW moderation for
bots, websites, APIs, and content pipelines.

---

## ✨ Features

- 🖼️ Image NSFW detection  
- 🎥 Video NSFW detection (frame-based analysis)  
- 🌐 URL scanning  
- ⚡ GPU acceleration (automatic CUDA detection)  
- 📦 Batch scanning  
- 💻 CLI support  
- 🤖 Telegram bot integration  
- 🔐 Policy-based actions (ALLOW / WARN / BLOCK / BAN)

---

## 🚀 Installation

```bash
pip install nsfwguard
```


---

## Example: Scan image 

```python
from nsfwguard import scan_image

result = scan_image("image.jpg")
print(result)
```

## Example: Scan a video file

```python
from nsfwguard import scan_video

result = scan_video("video.mp4")
print(result)
```

## Example: Scan any URL
```python
from nsfwguard import scan_url

result = scan_url("https://example.com/file.jpg")
print(result)
```
