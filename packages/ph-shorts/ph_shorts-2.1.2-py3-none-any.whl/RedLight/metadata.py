import subprocess
import shutil
import json
import requests
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime


class MetadataEditor:
    
    def __init__(self):
        self.ffmpeg_available = shutil.which("ffmpeg") is not None
        if not self.ffmpeg_available:
            raise RuntimeError("FFmpeg is required for metadata editing.")
            
    def SetMetadata(
        self,
        video_path: str,
        title: Optional[str] = None,
        artist: Optional[str] = None,
        album: Optional[str] = None,
        description: Optional[str] = None,
        genre: Optional[str] = None,
        date: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        input_path = Path(video_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
            
        if not output_path:
            temp_output = input_path.with_suffix(f".meta{input_path.suffix}")
        else:
            temp_output = Path(output_path)
            
        cmd = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-i', str(input_path),
            '-c', 'copy',
            '-map_metadata', '0'
        ]
        
        metadata = {
            'title': title,
            'artist': artist,
            'album': album,
            'comment': description,
            'genre': genre,
            'date': date
        }
        
        for key, value in metadata.items():
            if value:
                cmd.extend(['-metadata', f'{key}={value}'])
        
        cmd.append(str(temp_output))
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            if not output_path:
                shutil.move(str(temp_output), str(input_path))
                return str(input_path)
            
            return str(temp_output)
            
        except subprocess.CalledProcessError as e:
            if temp_output.exists():
                temp_output.unlink()
            raise RuntimeError(f"FFmpeg metadata error: {e.stderr}")

    def SetThumbnail(self, video_path: str, thumbnail_path: str, output_path: Optional[str] = None) -> str:
        input_path = Path(video_path)
        thumb_path = Path(thumbnail_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
        if not thumb_path.exists():
            raise FileNotFoundError(f"Thumbnail not found: {thumbnail_path}")
            
        if not output_path:
            temp_output = input_path.with_suffix(f".thumb{input_path.suffix}")
        else:
            temp_output = Path(output_path)
            
        cmd = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-i', str(input_path),
            '-i', str(thumb_path),
            '-map', '0', '-map', '1',
            '-c', 'copy',
            '-disposition:v:1', 'attached_pic',
            str(temp_output)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            if not output_path:
                shutil.move(str(temp_output), str(input_path))
                return str(input_path)
                
            return str(temp_output)
            
        except subprocess.CalledProcessError as e:
            if temp_output.exists():
                temp_output.unlink()
            raise RuntimeError(f"FFmpeg thumbnail error: {e.stderr}")


class MetadataSaver:
    
    def __init__(self, output_dir: str = "./downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def SaveMetadata(
        self,
        video_info: Dict[str, Any],
        video_path: str,
        format: str = "json"
    ) -> Optional[str]:
        video_file = Path(video_path)
        base_name = video_file.stem
        
        metadata = {
            "title": video_info.get("title", "Unknown"),
            "url": video_info.get("url", ""),
            "site": video_info.get("site", "Unknown"),
            "video_id": video_info.get("video_id", ""),
            "duration": video_info.get("duration", ""),
            "quality": video_info.get("quality", ""),
            "available_qualities": video_info.get("available_qualities", []),
            "description": video_info.get("description", ""),
            "uploader": video_info.get("uploader", ""),
            "upload_date": video_info.get("upload_date", ""),
            "views": video_info.get("views", 0),
            "rating": video_info.get("rating", 0),
            "tags": video_info.get("tags", []),
            "categories": video_info.get("categories", []),
            "thumbnail": video_info.get("thumbnail", ""),
            "downloaded_at": datetime.now().isoformat(),
            "file_path": str(video_path)
        }
        
        if format == "json":
            return self._save_json(metadata, video_file.parent / f"{base_name}.json")
        elif format == "nfo":
            return self._save_nfo(metadata, video_file.parent / f"{base_name}.nfo")
        
        return None
    
    def _save_json(self, metadata: Dict[str, Any], path: Path) -> str:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        return str(path)
    
    def _save_nfo(self, metadata: Dict[str, Any], path: Path) -> str:
        nfo_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<movie>
    <title>{self._escape_xml(metadata["title"])}</title>
    <originaltitle>{self._escape_xml(metadata["title"])}</originaltitle>
    <plot>{self._escape_xml(metadata["description"])}</plot>
    <runtime>{metadata["duration"]}</runtime>
    <thumb>{metadata["thumbnail"]}</thumb>
    <studio>{metadata["site"]}</studio>
    <director>{self._escape_xml(metadata["uploader"])}</director>
    <premiered>{metadata["upload_date"]}</premiered>
    <year>{metadata["upload_date"][:4] if metadata["upload_date"] else ""}</year>
    <rating>{metadata["rating"]}</rating>
    <votes>{metadata["views"]}</votes>
    <uniqueid type="site">{metadata["video_id"]}</uniqueid>
'''
        for tag in metadata.get("tags", []):
            nfo_content += f'    <tag>{self._escape_xml(tag)}</tag>\n'
        
        for genre in metadata.get("categories", []):
            nfo_content += f'    <genre>{self._escape_xml(genre)}</genre>\n'
        
        nfo_content += '</movie>'
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(nfo_content)
        
        return str(path)
    
    def _escape_xml(self, text: str) -> str:
        if not text:
            return ""
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))
    
    def DownloadThumbnail(
        self,
        thumbnail_url: str,
        video_path: str,
        session: Optional[requests.Session] = None
    ) -> Optional[str]:
        if not thumbnail_url:
            return None
        
        video_file = Path(video_path)
        thumb_path = video_file.parent / f"{video_file.stem}.jpg"
        
        try:
            sess = session or requests.Session()
            sess.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept-Encoding': 'gzip, deflate',
            })
            
            response = sess.get(thumbnail_url, timeout=30)
            response.raise_for_status()
            
            with open(thumb_path, 'wb') as f:
                f.write(response.content)
            
            return str(thumb_path)
        except Exception:
            return None


def SaveVideoMetadata(
    video_info: Dict[str, Any],
    video_path: str,
    format: str = "json",
    download_thumbnail: bool = True
) -> Dict[str, Optional[str]]:
    saver = MetadataSaver()
    result = {
        "metadata_path": None,
        "thumbnail_path": None
    }
    
    result["metadata_path"] = saver.SaveMetadata(video_info, video_path, format)
    
    if download_thumbnail and video_info.get("thumbnail"):
        result["thumbnail_path"] = saver.DownloadThumbnail(
            video_info["thumbnail"],
            video_path
        )
    
    return result

