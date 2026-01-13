import webbrowser
import threading
import sys
import os
import subprocess
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item


def open_dashboard(port):
    url = f'http://127.0.0.1:{port}'
    print(f"Opening dashboard at {url}...")
    
    # Try to open in App Mode (Chrome/Edge)
    # This creates a native-feeling window without address bar
    browsers = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\Application\msedge.exe")
    ]
    
    for browser in browsers:
        if os.path.exists(browser):
            try:
                subprocess.Popen([browser, f'--app={url}'])
                return
            except Exception:
                continue
    
    # Fallback to default browser
    webbrowser.open(url)


class RedLightTray:
    def __init__(self, port=5000, on_quit=None, on_open=None):
        self.port = port
        self.on_quit = on_quit
        self.on_open = on_open
        self.icon = None

    def create_image(self):
        # Generate an icon image (Red circle with white play button style)
        width = 64
        height = 64
        color1 = "#ff4757"  # RedLight accent color
        color2 = "#2f3542"  # Background
        
        image = Image.new('RGB', (width, height), color2)
        dc = ImageDraw.Draw(image)
        
        # Draw red circle
        dc.ellipse((8, 8, 56, 56), fill=color1)
        
        # Draw white play triangle
        # Points: (24, 20), (24, 44), (44, 32)
        dc.polygon([(26, 22), (26, 42), (42, 32)], fill="white")
        
        return image

    def on_open_dashboard(self, icon, item):
        if self.on_open:
            self.on_open(icon, item)
        else:
            open_dashboard(self.port)

    def on_exit(self, icon, item):
        icon.stop()
        if self.on_quit:
            self.on_quit(icon, item)
            
    def run(self):
        image = self.create_image()
        menu = (
            item('Open Dashboard', self.on_open_dashboard, default=True),
            item('Quit', self.on_exit)
        )
        
        self.icon = pystray.Icon("RedLightDL", image, "RedLight Downloader", menu)
        self.icon.run()

    def stop(self):
        if self.icon:
            self.icon.stop()


def run_tray(port=5000, on_quit=None, on_open=None):
    tray = RedLightTray(port, on_quit, on_open)
    tray.run()
