from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import yt_dlp
import os
import asyncio
from datetime import datetime, timedelta
import json
import aiofiles
from pathlib import Path

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 首先创建必要的目录
os.makedirs("downloads", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# 然后再挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

# 存储下载历史的文件
HISTORY_FILE = "download_history.json"

def load_download_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_download_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

@app.get("/")
async def home(request: Request):
    history = load_download_history()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "videos": history}
    )

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} GB"

@app.post("/download")
async def download_video(url: str = Form(...)):
    download_path = "downloads"
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'cookiesfrombrowser': ('chrome',),  # 使用 Chrome 浏览器的 cookies
        'concurrent_fragment_downloads': 1,
        'ignoreerrors': True,
        'no_color': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 获取视频信息
            info = ydl.extract_info(url, download=False)
            
            # 下载视频
            ydl.download([url])
            
            # 准备视频信息
            video_info = {
                'title': info['title'],
                'duration': str(timedelta(seconds=info['duration'])),
                'author': info['uploader'],
                'description': info.get('description', '')[:200] + '...',
                'url': url,
                'local_path': os.path.join(download_path, f"{info['title']}.{info['ext']}"),
                'download_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'file_size': format_size(os.path.getsize(os.path.join(download_path, f"{info['title']}.{info['ext']}"))),
                'thumbnail': info.get('thumbnail', ''),
            }
            
            # 更新下载历史
            history = load_download_history()
            history.append(video_info)
            save_download_history(history)
            
            return JSONResponse(content={"status": "success", "video_info": video_info})
            
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=400
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 