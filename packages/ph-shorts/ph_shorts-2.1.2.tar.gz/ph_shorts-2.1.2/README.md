# 🎬 RedLight DL

<div align="center">

![Version](https://img.shields.io/badge/version-2.1.2-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/ph-shorts?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/ph-shorts)

**Professional Adult Content Downloader with Style!** ✨

*A powerful, feature-rich downloader with a beautiful CLI, comprehensive Python API, and a Modern GUI*


[Installation](#-installation) • [Features](#-features) • [Usage CLI](#-usage-cli) • [Usage GUI](#-usage-gui-v212)

</div>

> **ℹ️ Note:** Formerly known as **PornHub-Shorts** → Renamed to **RedLight DL** to support multiple adult content platforms.

---

## 📦 Installation

### With [RedLightSetup.exe](https://github.com/diastom/RedLightDL/releases/download/v2.1.2/RedLightSetup.exe) file

```bash
just download and install it, no actions needed
```

### From PyPI ✅ 

```bash
pip install ph-shorts
```

### Quick Install (Linux/macOS)

```bash
chmod +x install.sh
./install.sh
```

### Quick Install (Windows)

```batch
install.bat
```


## 🌐 Supported Sites

- **PornHub** - HLS streaming downloads with full quality selection
- **YouPorn** - **[NEW]** Direct downloads with search support
- **Eporner** - Direct MP4 downloads with aria2c support
- **Spankbang** - Hybrid Delivery MP4/HLS with aria2c support (4K!)
- **XVideos** - Multi-quality MP4/HLS downloads with intelligent fallback
- **xHamster** - HLS streaming with multi-quality and geo-fallback support
- **XNXX** - Multi-quality MP4/HLS downloads (same structure as XVideos)

---

## ✨ Features

- **Multi-Site Support** - Download from 7 major adult content sites
- **Automatic Site Detection** - Just paste any supported URL
- **Beautiful GUI** - Modern, Glassmorphism design with React & Python
- **Advanced Queue** - Priority-based download queue with Pause/Resume
- **Fast Downloads** - Multi-threaded + aria2c support (up to 16 connections)
- **Quality Selection** - Choose from available qualities (up to 4K!)
- **Batch Downloads** - Download multiple videos concurrently
- **Playlist/Channel Support** - Download entire channels
- **Advanced Search** - Integrated search for supported sites
- **Favorites & History** - Manage your favorite videos and view download history
- **Proxy Manager** - Rotating proxy support (HTTP/HTTPS/SOCKS)
- **Rate Limiting** - Smart limits to prevent temporary IP bans
- **System Integration** - System Tray icon and Desktop Notifications (Windows)
- **Python API** - Use as a library for automation

### NEW in v2.1.2 ✨
- **Queue Management** - Reorder, prioritize, and schedule downloads
- **Proxy Rotation** - Automatically switch proxies on failure
- **Search & Favorites** - Built-in search engine and folders for favorites
- **System Tray** - Minimize to tray background running
- **Drag & Drop** - Drag URLs directly into the app
- **Theme Support** - Light/Dark mode toggle


---

## 🚀 Usage (GUI) v2.1.2+

Download the [RedLightSetup.exe](https://github.com/diastom/RedLightDL/releases) file and install it.

**Key Capabilities:**
1. **Dashboard**: View real-time stats and download speeds.
2. **Search**: Search specific sites or all sites at once.
3. **Queue**: Manage your downloads, change priorities, or pause the queue.
4. **Extras**: Use the Batch Downloader for multiple links or configure Proxies.

<img width="1919" height="1109" alt="Screenshot 2025-12-12 152928" src="https://github.com/user-attachments/assets/b0069142-93ff-4fe8-abe2-58502582e0d1" />


<img width="1919" height="1107" alt="Screenshot 2025-12-12 153151" src="https://github.com/user-attachments/assets/e1209e49-744e-45b1-8a79-a08282541914" />



## 🚀 Usage (CLI)

### Interactive Mode (Recommended for beginners)

Simply run without arguments:

```bash
ph-shorts
```

You'll get a beautiful interactive menu:

```
╔══════════════════════════════════════════════════════════════════╗
║  ██████╗ ███████╗██████╗ ██╗     ██╗ ██████╗ ██╗  ██╗████████╗   ║
║  ██╔══██╗██╔════╝██╔══██╗██║     ██║██╔════╝ ██║  ██║╚══██╔══╝   ║
║  ██████╔╝█████╗  ██║  ██║██║     ██║██║  ███╗███████║   ██║      ║
║  ██╔══██╗██╔══╝  ██║  ██║██║     ██║██║   ██║██╔══██║   ██║      ║
║  ██║  ██║███████╗██████╔╝███████╗██║╚██████╔╝██║  ██║   ██║      ║
║  ╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝      ║
║          Professional Adult Content Downloader                   ║
╚══════════════════════════════════════════════════════════════════╝
                    version 2.1.2 • RedLight DL
```


### Command Line Mode

```bash
# Download from any supported site
ph-shorts "VIDEO_URL"

# Specify quality
ph-shorts "URL" -q 720

# Custom output
ph-shorts "URL" -o my_video.mp4

# Use proxy
ph-shorts "URL" -p http://127.0.0.1:1080
```

---

## 📚 Documentation

Complete documentation available in [`docs/`](docs/):

- **[Quick Start Guide](docs/QuickStart.md)** - Get started in 5 minutes
- **[Multi-Site Guide](docs/MultiSite.md)** - Complete multi-site guide
- **[API Reference](docs/API.md)** - Function documentation
- **[Examples](docs/Examples.md)** - Code examples
- **[Advanced Usage](docs/Advanced.md)** - Advanced topics

---

## 🔧 Requirements

### Required
- Python 3.10 or higher
- Internet connection

### Optional (Recommended)
- **FFmpeg** - For automatic MP4 conversion
  - **Ubuntu/Debian**: `sudo apt install ffmpeg`
  - **macOS**: `brew install ffmpeg`
  - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚖️ Disclaimer

This tool is for educational purposes only. Please respect copyright laws and the terms of service of the websites you download from. The developers are not responsible for any misuse of this software.

---

<div align="center">

**Made with ❤️ by AI (Google Antigravity)**

If this tool helped you, consider giving it a ⭐ on GitHub!

[GitHub](https://github.com/diastom/RedLightDL) • [PyPI](https://pypi.org/project/ph-shorts/) • [Documentation](docs/)

</div>
