import os, uuid, subprocess
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

if os.getenv("COOKIES_TXT"):
    with open("/tmp/cookies.txt", "w") as f:
        f.write(os.getenv("COOKIES_TXT"))

@app.get("/")
def health():
    return {"status": "online"}

@app.get("/clip")
def clip(url: str, start: str, end: str, background_tasks: BackgroundTasks):
    out = f"/tmp/{uuid.uuid4()}.mp4"
    cmd = [
        "yt-dlp",
        "--download-sections", f"*{start}-{end}",
        "--force-keyframes-at-cuts",
        "-f", "best[height<=480][ext=mp4]/best[height<=720][ext=mp4]",
        "-o", out,
        url,
    ]
    if os.path.exists("/tmp/cookies.txt"):
        cmd.extend(["--cookies", "/tmp/cookies.txt"])
    try:
        subprocess.run(cmd, check=True, timeout=180)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    background_tasks.add_task(lambda p: os.path.exists(p) and os.remove(p), out)
    return FileResponse(out, media_type="video/mp4", filename="clip.mp4")
