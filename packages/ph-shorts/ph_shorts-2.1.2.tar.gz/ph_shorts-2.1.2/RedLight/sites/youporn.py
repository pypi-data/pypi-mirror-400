import re
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from bs4 import BeautifulSoup

from .base import BaseSiteDownloader, BaseSiteSearch


class YouPornDownloader(BaseSiteDownloader):
    
    URL_PATTERN = r'(?:https?://)?(?:www\.)?youporn\.com/watch/(\d+)'
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
        })
    
    @classmethod
    def is_supported_url(cls, url: str) -> bool:
        return bool(re.search(cls.URL_PATTERN, url))
    
    @staticmethod
    def get_site_name() -> str:
        return "youporn"
    
    def ExtractVideoId(self, url: str) -> Optional[str]:
        match = re.search(self.URL_PATTERN, url)
        return match.group(1) if match else None
    
    def GetMediaDefinition(self, url: str) -> tuple:
        response = self.session.get(url)
        response.raise_for_status()
        html = response.text
        
        title_match = re.search(r'<title>([^<]+)</title>', html)
        title = title_match.group(1).replace(' - YouPorn', '').strip() if title_match else 'youporn_video'
        title = re.sub(r'[<>:"/\\|?*]', '_', title)
        
        media_def_match = re.search(r'mediaDefinition\s*:\s*(\[.*?\])', html, re.DOTALL)
        if not media_def_match:
            media_def_match = re.search(r'"mediaDefinition"\s*:\s*(\[.*?\])', html, re.DOTALL)
        
        if not media_def_match:
            raise ValueError("Could not find mediaDefinition in page")
        
        try:
            media_def_str = media_def_match.group(1)
            media_def_str = re.sub(r',\s*]', ']', media_def_str)
            media_definition = json.loads(media_def_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse mediaDefinition: {e}")
        
        return title, media_definition
    
    def GetQualities(self, media_definition: List[Dict]) -> Dict[int, str]:
        qualities = {}
        
        mp4_entry = next((m for m in media_definition if m.get('format') == 'mp4'), None)
        if mp4_entry and mp4_entry.get('videoUrl'):
            try:
                api_url = mp4_entry['videoUrl']
                response = self.session.get(api_url)
                if response.ok:
                    mp4_data = response.json()
                    for item in mp4_data:
                        if 'quality' in item and 'videoUrl' in item:
                            quality = int(item['quality'])
                            qualities[quality] = item['videoUrl']
            except Exception:
                pass
        
        if not qualities:
            for item in media_definition:
                if 'quality' in item and 'videoUrl' in item:
                    if item['videoUrl'] and not item.get('remote'):
                        try:
                            quality = int(item['quality'])
                            qualities[quality] = item['videoUrl']
                        except ValueError:
                            pass
        
        return qualities
    
    def download(
        self,
        url: str,
        quality: str = "best",
        output_dir: str = "./downloads",
        filename: Optional[str] = None,
        keep_original: bool = False,
        proxy: Optional[str] = None,
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> str:
        
        if proxy:
            self.session.proxies = {'http': proxy, 'https': proxy}
        
        title, media_definition = self.GetMediaDefinition(url)
        qualities = self.GetQualities(media_definition)
        
        if not qualities:
            raise ValueError("No downloadable qualities found")
        
        sorted_qualities = sorted(qualities.keys(), reverse=True)
        
        if quality == "best":
            selected_quality = sorted_qualities[0]
        elif quality == "worst":
            selected_quality = sorted_qualities[-1]
        else:
            try:
                requested = int(quality.replace('p', ''))
                selected_quality = min(sorted_qualities, key=lambda x: abs(x - requested))
            except ValueError:
                selected_quality = sorted_qualities[0]
        
        video_url = qualities[selected_quality]
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        if filename:
            output_file = output_path / filename
        else:
            output_file = output_path / f"{title}_{selected_quality}p.mp4"
        
        response = self.session.get(video_url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if on_progress and total_size:
                        should_continue = on_progress(downloaded, total_size)
                        if should_continue is False:
                            raise Exception("Download cancelled")
        
        return str(output_file)
    
    def get_info(self, url: str) -> Dict[str, Any]:
        video_id = self.ExtractVideoId(url)
        title, media_definition = self.GetMediaDefinition(url)
        qualities = self.GetQualities(media_definition)
        
        return {
            "title": title,
            "available_qualities": sorted(qualities.keys(), reverse=True),
            "video_id": video_id,
            "site": "youporn"
        }
    
    def list_qualities(self, url: str) -> List[int]:
        info = self.get_info(url)
        return info["available_qualities"]


class YouPornSearch(BaseSiteSearch):
    
    def __init__(self):
        self.base_url = "https://www.youporn.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
        })
    
    def search(
        self,
        query: str,
        page: int = 1,
        sort_by: str = "relevance",
        duration: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        
        search_url = f"{self.base_url}/search/"
        params = {
            'query': query,
            'page': page
        }
        
        if sort_by == "newest":
            params['sort'] = 'time'
        elif sort_by == "rating":
            params['sort'] = 'rating'
        elif sort_by == "views":
            params['sort'] = 'views'
        
        if duration:
            if duration == "short":
                params['duration'] = '1-5min'
            elif duration == "medium":
                params['duration'] = '5-20min'
            elif duration == "long":
                params['duration'] = '20min_plus'
        
        try:
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
        except Exception:
            return []
        
        return self.ParseResults(response.text)
    
    def ParseResults(self, html: str) -> List[Dict[str, Any]]:
        results = []
        soup = BeautifulSoup(html, 'html.parser')
        
        video_items = soup.select('.video-box, .videoBox, [data-video-id]')
        
        for item in video_items[:20]:
            try:
                link = item.select_one('a[href*="/watch/"]')
                if not link:
                    continue
                
                href = link.get('href', '')
                if not href.startswith('http'):
                    href = self.base_url + href
                
                title_elem = item.select_one('.video-title, .title, h3, h4')
                title = title_elem.get_text(strip=True) if title_elem else 'Unknown'
                
                duration_elem = item.select_one('.video-duration, .duration, time')
                duration = duration_elem.get_text(strip=True) if duration_elem else ''
                
                thumb_elem = item.select_one('img')
                thumbnail = thumb_elem.get('data-src') or thumb_elem.get('src') if thumb_elem else ''
                
                views_elem = item.select_one('.video-views, .views')
                views = views_elem.get_text(strip=True) if views_elem else ''
                
                results.append({
                    'title': title,
                    'url': href,
                    'duration': duration,
                    'thumbnail': thumbnail,
                    'views': views,
                    'site': 'youporn'
                })
            except Exception:
                continue
        
        return results
    
    def GetTrending(self, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            response = self.session.get(f"{self.base_url}/popular/")
            response.raise_for_status()
            return self.ParseResults(response.text)[:limit]
        except Exception:
            return []
    
    def get_search_filters(self) -> Dict[str, List[str]]:
        return {
            "sort_by": ["relevance", "newest", "rating", "views"],
            "duration": ["short", "medium", "long"]
        }
    
    @staticmethod
    def get_site_name() -> str:
        return "youporn"
