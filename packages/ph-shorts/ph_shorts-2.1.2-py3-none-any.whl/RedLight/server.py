from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os
import traceback

# Ensure we can import from local package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from RedLight.api import (
    GetActiveDownloads,
    StartResumableDownload,
    GetVideoInfo,
    CancelDownload,
    GetStatistics,
    GetDownloadHistory
)
from RedLight.config import ConfigManager

app = Flask(__name__) # Initialize first to access helpers if needed, but we'll override static config

def get_static_folder():
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app 
        # path into variable _MEIPASS.
        # For 'onedir' mode, we expect assets in the same dir as executable/script
        base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(os.path.abspath(__file__))
        
        # When using --add-data, folders are preserved. 
        # We mapped "gui/client/dist" -> "gui/client/dist"
        return os.path.join(base_path, 'gui', 'client', 'dist')
    else:
        # Normal python execution
        return '../gui/client/dist'

static_folder = get_static_folder()
app = Flask(__name__, static_folder=static_folder, static_url_path='/')
CORS(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        stats = GetStatistics()
        return jsonify(stats)
    except Exception as e:
        traceback.print_exc()
        try:
            with open(os.path.expanduser("~/.RedLight/error.log"), "a") as f:
                f.write(traceback.format_exc() + "\n")
        except:
            pass
        return jsonify({"error": str(e)}), 500

@app.route('/api/downloads/history', methods=['GET'])
def get_history():
    try:
        limit = int(request.args.get('limit', 10))
        history = GetDownloadHistory(limit=limit)
        return jsonify(history)
    except Exception as e:
        traceback.print_exc()
        try:
            with open(os.path.expanduser("~/.RedLight/error.log"), "a") as f:
                f.write(traceback.format_exc() + "\n")
        except:
            pass
        return jsonify({"error": str(e)}), 500

@app.route('/api/downloads/active', methods=['GET'])
def get_active():
    try:
        active = GetActiveDownloads()
        return jsonify(active)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/download', methods=['POST'])
def start_download():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', 'best')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    try:
        download_id = StartResumableDownload(url, quality=quality)
        return jsonify({"success": True, "id": download_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cancel', methods=['POST'])
def cancel_download():
    data = request.json
    download_id = data.get('download_id')
    if not download_id:
        return jsonify({"error": "Download ID is required"}), 400
    try:
        success = CancelDownload(download_id)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/info', methods=['GET'])
def get_info():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400
    try:
        info = GetVideoInfo(url)
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    try:
        from RedLight.config import GetConfig
        config = GetConfig()
        return jsonify(config.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/config', methods=['POST'])
def update_config():
    try:
        from RedLight.config import GetConfigManager, Config
        data = request.json
        cm = GetConfigManager()
        current_config = cm.get()
        
        if 'downloadPath' in data:
            current_config.download.output_directory = data['downloadPath']
        if 'maxConcurrent' in data:
            current_config.download.max_concurrent = int(data['maxConcurrent'])
        if 'quality' in data:
            current_config.download.default_quality = data['quality']
        if 'proxy' in data:
            current_config.download.proxy = data['proxy']
        if 'speedLimit' in data:
            current_config.download.speed_limit = data['speedLimit']
        if 'keepTs' in data:
            current_config.download.keep_ts = data['keepTs']
        if 'downloadSubtitles' in data:
            current_config.download.subtitles = data['downloadSubtitles']
        
        cm.save(current_config)
        return jsonify({"success": True, "config": current_config.to_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_videos():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Query is required"}), 400
    try:
        from RedLight.multi_search import MultiSiteSearch
        engine = MultiSiteSearch()
        results = engine.search_all(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/playlist', methods=['GET'])
def get_playlist_videos():
    """Get list of videos from a channel/playlist URL"""
    url = request.args.get('url')
    limit = int(request.args.get('limit', 10))
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    try:
        from RedLight.playlist import PlaylistDownloader
        downloader = PlaylistDownloader()
        videos = downloader.GetChannelVideos(url, limit=limit)
        return jsonify({"videos": videos, "count": len(videos)})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/playlist/download', methods=['POST'])
def download_playlist():
    """Start downloading all videos from a playlist"""
    data = request.json
    url = data.get('url')
    limit = int(data.get('limit', 10))
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    try:
        from RedLight.playlist import PlaylistDownloader
        downloader = PlaylistDownloader()
        videos = downloader.GetChannelVideos(url, limit=limit)
        
        download_ids = []
        for video_url in videos:
            try:
                download_id = StartResumableDownload(video_url)
                download_ids.append({"url": video_url, "id": download_id})
            except Exception as e:
                download_ids.append({"url": video_url, "error": str(e)})
        
        return jsonify({"success": True, "downloads": download_ids})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/queue', methods=['GET'])
def get_queue():
    try:
        from RedLight.queue_manager import GetQueueManager
        manager = GetQueueManager()
        return jsonify(manager.GetQueueStatus())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/queue/add', methods=['POST'])
def add_to_queue():
    try:
        from RedLight.queue_manager import GetQueueManager, Priority
        data = request.json
        url = data.get('url')
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        priority_map = {"high": Priority.HIGH, "normal": Priority.NORMAL, "low": Priority.LOW}
        priority = priority_map.get(data.get('priority', 'normal'), Priority.NORMAL)
        
        manager = GetQueueManager()
        item_id = manager.AddToQueue(
            url=url,
            quality=data.get('quality', 'best'),
            priority=priority,
            title=data.get('title', ''),
            site=data.get('site', '')
        )
        return jsonify({"success": True, "id": item_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/queue/remove', methods=['POST'])
def remove_from_queue():
    try:
        from RedLight.queue_manager import GetQueueManager
        data = request.json
        item_id = data.get('id')
        if not item_id:
            return jsonify({"error": "ID is required"}), 400
        
        manager = GetQueueManager()
        success = manager.RemoveFromQueue(item_id)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/queue/pause', methods=['POST'])
def pause_queue():
    try:
        from RedLight.queue_manager import GetQueueManager
        GetQueueManager().PauseQueue()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/queue/resume', methods=['POST'])
def resume_queue():
    try:
        from RedLight.queue_manager import GetQueueManager
        GetQueueManager().ResumeQueue()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    try:
        from RedLight.favorites import GetFavoritesManager
        folder = request.args.get('folder')
        limit = int(request.args.get('limit', 100))
        manager = GetFavoritesManager()
        return jsonify(manager.GetFavorites(folder=folder, limit=limit))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/favorites/add', methods=['POST'])
def add_favorite():
    try:
        from RedLight.favorites import GetFavoritesManager
        data = request.json
        url = data.get('url')
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        manager = GetFavoritesManager()
        success = manager.AddFavorite(
            url=url,
            title=data.get('title', ''),
            thumbnail=data.get('thumbnail', ''),
            duration=data.get('duration', ''),
            site=data.get('site', ''),
            folder=data.get('folder', 'default')
        )
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/favorites/remove', methods=['POST'])
def remove_favorite():
    try:
        from RedLight.favorites import GetFavoritesManager
        data = request.json
        url = data.get('url')
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        manager = GetFavoritesManager()
        success = manager.RemoveFavorite(url)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/favorites/check', methods=['GET'])
def check_favorite():
    try:
        from RedLight.favorites import GetFavoritesManager
        url = request.args.get('url')
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        manager = GetFavoritesManager()
        return jsonify({"is_favorite": manager.IsFavorite(url)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/favorites/folders', methods=['GET'])
def get_folders():
    try:
        from RedLight.favorites import GetFavoritesManager
        return jsonify(GetFavoritesManager().GetFolders())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search/history', methods=['GET'])
def get_search_history():
    try:
        from RedLight.favorites import GetFavoritesManager
        limit = int(request.args.get('limit', 20))
        return jsonify(GetFavoritesManager().GetSearchHistory(limit))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search/history/clear', methods=['POST'])
def clear_search_history():
    try:
        from RedLight.favorites import GetFavoritesManager
        GetFavoritesManager().ClearSearchHistory()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/proxy', methods=['GET'])
def get_proxy_status():
    try:
        from RedLight.proxy_manager import GetProxyManager
        manager = GetProxyManager()
        return jsonify({
            "status": manager.GetStatus(),
            "proxies": manager.GetProxyList()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/proxy/add', methods=['POST'])
def add_proxy():
    try:
        from RedLight.proxy_manager import GetProxyManager
        data = request.json
        proxy_url = data.get('url')
        if not proxy_url:
            return jsonify({"error": "Proxy URL is required"}), 400
        
        manager = GetProxyManager()
        success = manager.AddProxyFromUrl(proxy_url)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/proxy/remove', methods=['POST'])
def remove_proxy():
    try:
        from RedLight.proxy_manager import GetProxyManager
        data = request.json
        index = data.get('index')
        if index is None:
            return jsonify({"error": "Index is required"}), 400
        
        manager = GetProxyManager()
        success = manager.RemoveProxy(int(index))
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/proxy/toggle', methods=['POST'])
def toggle_proxy():
    try:
        from RedLight.proxy_manager import GetProxyManager
        data = request.json
        enabled = data.get('enabled', False)
        
        manager = GetProxyManager()
        if enabled:
            manager.Enable()
        else:
            manager.Disable()
        return jsonify({"success": True, "enabled": manager.IsEnabled()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/rate-limit', methods=['GET'])
def get_rate_limit_status():
    try:
        from RedLight.rate_limiter import GetRateLimiter
        return jsonify(GetRateLimiter().GetStatus())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting RedLight API Server on port 5000...")
    app.run(host='127.0.0.1', port=5000, debug=True)

