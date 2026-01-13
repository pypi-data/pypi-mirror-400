import threading
import time
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import IntEnum
from datetime import datetime
import heapq


class Priority(IntEnum):
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass(order=True)
class QueueItem:
    priority: int
    created_at: float = field(compare=True)
    item_id: str = field(compare=False)
    url: str = field(compare=False)
    quality: str = field(compare=False, default="best")
    status: str = field(compare=False, default="pending")
    title: str = field(compare=False, default="")
    site: str = field(compare=False, default="")
    scheduled_time: Optional[datetime] = field(compare=False, default=None)


class DownloadQueueManager:
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.db_path = Path.home() / ".RedLight" / "queue.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._queue: List[QueueItem] = []
        self._active_downloads: Dict[str, QueueItem] = {}
        self._max_concurrent = 3
        self._paused = False
        self._running = False
        self._worker_thread = None
        self._callbacks: Dict[str, List[Callable]] = {
            'on_start': [],
            'on_complete': [],
            'on_error': [],
            'on_progress': []
        }
        
        self._init_db()
        self._load_pending()
        self._initialized = True
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS queue (
                item_id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                quality TEXT DEFAULT 'best',
                priority INTEGER DEFAULT 2,
                status TEXT DEFAULT 'pending',
                title TEXT,
                site TEXT,
                scheduled_time TEXT,
                created_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                error TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def _load_pending(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM queue WHERE status IN ('pending', 'paused') ORDER BY priority, created_at")
        rows = c.fetchall()
        conn.close()
        
        for row in rows:
            item = QueueItem(
                priority=row[3],
                created_at=datetime.fromisoformat(row[8]).timestamp() if row[8] else time.time(),
                item_id=row[0],
                url=row[1],
                quality=row[2],
                status=row[4],
                title=row[5] or "",
                site=row[6] or "",
                scheduled_time=datetime.fromisoformat(row[7]) if row[7] else None
            )
            heapq.heappush(self._queue, item)
    
    def AddToQueue(
        self,
        url: str,
        quality: str = "best",
        priority: Priority = Priority.NORMAL,
        title: str = "",
        site: str = "",
        scheduled_time: Optional[datetime] = None
    ) -> str:
        import uuid
        item_id = str(uuid.uuid4())[:8]
        
        item = QueueItem(
            priority=priority.value,
            created_at=time.time(),
            item_id=item_id,
            url=url,
            quality=quality,
            title=title,
            site=site,
            scheduled_time=scheduled_time
        )
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO queue (item_id, url, quality, priority, status, title, site, scheduled_time, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item_id, url, quality, priority.value, 'pending', title, site,
            scheduled_time.isoformat() if scheduled_time else None,
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
        
        heapq.heappush(self._queue, item)
        
        if self._running and not self._paused:
            self._process_next()
        
        return item_id
    
    def RemoveFromQueue(self, item_id: str) -> bool:
        self._queue = [item for item in self._queue if item.item_id != item_id]
        heapq.heapify(self._queue)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM queue WHERE item_id = ?", (item_id,))
        affected = c.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def ChangePriority(self, item_id: str, priority: Priority) -> bool:
        for item in self._queue:
            if item.item_id == item_id:
                self._queue.remove(item)
                item.priority = priority.value
                heapq.heappush(self._queue, item)
                
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                c.execute("UPDATE queue SET priority = ? WHERE item_id = ?", (priority.value, item_id))
                conn.commit()
                conn.close()
                return True
        return False
    
    def MoveToTop(self, item_id: str) -> bool:
        return self.ChangePriority(item_id, Priority.HIGH)
    
    def GetQueueStatus(self) -> Dict[str, Any]:
        return {
            "pending": len(self._queue),
            "active": len(self._active_downloads),
            "paused": self._paused,
            "max_concurrent": self._max_concurrent,
            "items": [
                {
                    "id": item.item_id,
                    "url": item.url,
                    "title": item.title,
                    "priority": item.priority,
                    "status": item.status,
                    "site": item.site
                }
                for item in sorted(self._queue)
            ]
        }
    
    def GetActiveDownloads(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": item.item_id,
                "url": item.url,
                "title": item.title,
                "site": item.site,
                "status": "downloading"
            }
            for item in self._active_downloads.values()
        ]
    
    def PauseQueue(self):
        self._paused = True
    
    def ResumeQueue(self):
        self._paused = False
        if self._running:
            self._process_next()
    
    def SetMaxConcurrent(self, max_concurrent: int):
        self._max_concurrent = max(1, min(10, max_concurrent))
    
    def Start(self):
        if not self._running:
            self._running = True
            self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self._worker_thread.start()
    
    def Stop(self):
        self._running = False
    
    def _worker_loop(self):
        while self._running:
            if not self._paused:
                self._process_next()
            time.sleep(1)
    
    def _process_next(self):
        if self._paused or len(self._active_downloads) >= self._max_concurrent:
            return
        
        if not self._queue:
            return
        
        now = datetime.now()
        for item in sorted(self._queue):
            if item.scheduled_time and item.scheduled_time > now:
                continue
            
            if len(self._active_downloads) >= self._max_concurrent:
                break
            
            self._queue.remove(item)
            heapq.heapify(self._queue)
            self._start_download(item)
    
    def _start_download(self, item: QueueItem):
        self._active_downloads[item.item_id] = item
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE queue SET status = 'downloading', started_at = ? WHERE item_id = ?",
                 (datetime.now().isoformat(), item.item_id))
        conn.commit()
        conn.close()
        
        for callback in self._callbacks['on_start']:
            try:
                callback(item.item_id, item.url)
            except Exception:
                pass
        
        thread = threading.Thread(target=self._download_worker, args=(item,), daemon=True)
        thread.start()
    
    def _download_worker(self, item: QueueItem):
        try:
            from .api import DownloadVideo
            
            result = DownloadVideo(
                url=item.url,
                quality=item.quality
            )
            
            self._complete_download(item.item_id, result)
        except Exception as e:
            self._fail_download(item.item_id, str(e))
    
    def _complete_download(self, item_id: str, result_path: str):
        if item_id in self._active_downloads:
            del self._active_downloads[item_id]
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE queue SET status = 'completed', completed_at = ? WHERE item_id = ?",
                 (datetime.now().isoformat(), item_id))
        conn.commit()
        conn.close()
        
        for callback in self._callbacks['on_complete']:
            try:
                callback(item_id, result_path)
            except Exception:
                pass
        
        self._process_next()
    
    def _fail_download(self, item_id: str, error: str):
        if item_id in self._active_downloads:
            del self._active_downloads[item_id]
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE queue SET status = 'failed', error = ? WHERE item_id = ?", (error, item_id))
        conn.commit()
        conn.close()
        
        for callback in self._callbacks['on_error']:
            try:
                callback(item_id, error)
            except Exception:
                pass
        
        self._process_next()
    
    def OnStart(self, callback: Callable):
        self._callbacks['on_start'].append(callback)
    
    def OnComplete(self, callback: Callable):
        self._callbacks['on_complete'].append(callback)
    
    def OnError(self, callback: Callable):
        self._callbacks['on_error'].append(callback)
    
    def ClearCompleted(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM queue WHERE status IN ('completed', 'failed')")
        conn.commit()
        conn.close()
    
    def GetHistory(self, limit: int = 50) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT item_id, url, title, site, status, completed_at, error 
            FROM queue 
            WHERE status IN ('completed', 'failed')
            ORDER BY completed_at DESC
            LIMIT ?
        ''', (limit,))
        rows = c.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "url": row[1],
                "title": row[2],
                "site": row[3],
                "status": row[4],
                "completed_at": row[5],
                "error": row[6]
            }
            for row in rows
        ]


_queue_manager: Optional[DownloadQueueManager] = None


def GetQueueManager() -> DownloadQueueManager:
    global _queue_manager
    if _queue_manager is None:
        _queue_manager = DownloadQueueManager()
    return _queue_manager
