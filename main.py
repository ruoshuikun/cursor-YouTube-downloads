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

# 挂载静态文件目录
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
        'format': 'best[ext=mp4]/best',
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        'verbose': True,
        'cookiesfrombrowser': ('chrome',),
        'concurrent_fragment_downloads': 1,
        'ignoreerrors': True,
        'no_color': True,
    }
    
    try:
        print(f"开始下载视频: {url}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # 获取视频信息
                print("正在获取视频信息...")
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise ValueError("无法获取视频信息")
                
                # 生成安全的文件名 {video_id}_{YYYYMMDD_HHMMSS}.mp4
                video_id = info['id']
                current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_filename = f"{video_id}_{current_time}.mp4"
                
                print(f"使用的文件名: {safe_filename}")
                
                # 设置新的下载选项，使用安全的文件名
                full_path = os.path.join(download_path, safe_filename)
                ydl_opts['outtmpl'] = full_path
                
                print(f"下载路径: {full_path}")
                
                # 使用新的选项下载视频
                with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                    print("开始下载...")
                    ydl2.download([url])
                
                if not os.path.exists(full_path):
                    raise FileNotFoundError(f"下载完成后文件不存在: {full_path}")
                
                # 准备视频信息
                video_info = {
                    'title': info['title'],
                    'duration': str(timedelta(seconds=info['duration'])),
                    'author': info['uploader'],
                    'description': info.get('description', '')[:200] + '...',
                    'url': url,
                    'local_path': f"/downloads/{safe_filename}",
                    'download_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'file_size': format_size(os.path.getsize(full_path)),
                    'thumbnail': info.get('thumbnail', ''),
                }
                
                # 更新下载历史
                history = load_download_history()
                history.append(video_info)
                save_download_history(history)
                
                print("下载成功完成")
                return JSONResponse(content={"status": "success", "video_info": video_info})
                
            except Exception as inner_e:
                print(f"内部错误: {str(inner_e)}")
                raise inner_e
            
    except Exception as e:
        error_msg = f"下载失败: {str(e)}"
        print(error_msg)
        return JSONResponse(
            content={"status": "error", "message": error_msg},
            status_code=400
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 