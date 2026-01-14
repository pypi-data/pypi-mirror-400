from fastapi import FastAPI, UploadFile
import tempfile, shutil, asyncio
from .image import scan_image
from .video import scan_video

app = FastAPI(title="NSFWDetector API")

@app.post("/scan/image")
async def scan_img(file: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        return await asyncio.to_thread(scan_image, tmp.name)

@app.post("/scan/video")
async def scan_vid(file: UploadFile):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        return await asyncio.to_thread(scan_video, tmp.name)
