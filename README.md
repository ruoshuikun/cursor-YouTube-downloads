# YouTube 视频下载器

一个简单的 YouTube 视频下载网站，使用 FastAPI + Jinja2 + yt-dlp + TailwindCSS 构建。

## 功能特点

- 支持输入 YouTube 视频链接进行下载
- 美观的用户界面，响应式设计
- 显示下载进度
- 支持视频预览播放
- 显示详细的视频信息（标题、时长、作者等）
- 本地视频管理

## 安装说明

1. 克隆项目到本地：
```bash
git clone [项目地址]
cd YouTube-download
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行项目：
```bash
python main.py
```

4. 打开浏览器访问：
```
http://localhost:8000
```

## 使用说明

1. 在输入框中粘贴 YouTube 视频链接
2. 点击"下载视频"按钮
3. 等待下载完成
4. 下载完成后可在页面下方查看和播放视频

## 目录结构

```
.
├── main.py              # 后端主程序
├── requirements.txt     # 项目依赖
├── templates/          
│   └── index.html      # 前端模板
├── static/             # 静态文件目录
└── downloads/          # 下载的视频存储目录
```

## 注意事项

- 确保有足够的磁盘空间存储下载的视频
- 需要稳定的网络连接
- 请遵守 YouTube 的使用条款和版权规定 