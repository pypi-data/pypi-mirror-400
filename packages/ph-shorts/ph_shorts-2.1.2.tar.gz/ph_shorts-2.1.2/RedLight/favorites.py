import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class FavoritesManager:
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.db_path = Path.home() / ".RedLight" / "favorites.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._initialized = True
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                title TEXT,
                thumbnail TEXT,
                duration TEXT,
                site TEXT,
                folder TEXT DEFAULT 'default',
                added_at TEXT
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TEXT
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                site TEXT,
                results_count INTEGER DEFAULT 0,
                searched_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def AddFavorite(
        self,
        url: str,
        title: str = "",
        thumbnail: str = "",
        duration: str = "",
        site: str = "",
        folder: str = "default"
    ) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO favorites (url, title, thumbnail, duration, site, folder, added_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (url, title, thumbnail, duration, site, folder, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def RemoveFavorite(self, url: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM favorites WHERE url = ?", (url,))
        affected = c.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    def GetFavorites(self, folder: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if folder:
            c.execute('''
                SELECT url, title, thumbnail, duration, site, folder, added_at 
                FROM favorites WHERE folder = ? 
                ORDER BY added_at DESC LIMIT ?
            ''', (folder, limit))
        else:
            c.execute('''
                SELECT url, title, thumbnail, duration, site, folder, added_at 
                FROM favorites 
                ORDER BY added_at DESC LIMIT ?
            ''', (limit,))
        
        rows = c.fetchall()
        conn.close()
        
        return [
            {
                "url": row[0],
                "title": row[1],
                "thumbnail": row[2],
                "duration": row[3],
                "site": row[4],
                "folder": row[5],
                "added_at": row[6]
            }
            for row in rows
        ]
    
    def IsFavorite(self, url: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT 1 FROM favorites WHERE url = ?", (url,))
        result = c.fetchone()
        conn.close()
        return result is not None
    
    def CreateFolder(self, name: str) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("INSERT INTO folders (name, created_at) VALUES (?, ?)", 
                     (name, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def GetFolders(self) -> List[str]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT name FROM folders ORDER BY name")
        rows = c.fetchall()
        conn.close()
        return ["default"] + [row[0] for row in rows]
    
    def MoveToFolder(self, url: str, folder: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE favorites SET folder = ? WHERE url = ?", (folder, url))
        affected = c.rowcount
        conn.commit()
        conn.close()
        return affected > 0
    
    def AddSearchHistory(self, query: str, site: str = "", results_count: int = 0) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                INSERT INTO search_history (query, site, results_count, searched_at)
                VALUES (?, ?, ?, ?)
            ''', (query, site, results_count, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def GetSearchHistory(self, limit: int = 20) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT DISTINCT query, site, results_count, searched_at 
            FROM search_history 
            ORDER BY searched_at DESC LIMIT ?
        ''', (limit,))
        rows = c.fetchall()
        conn.close()
        
        return [
            {
                "query": row[0],
                "site": row[1],
                "results_count": row[2],
                "searched_at": row[3]
            }
            for row in rows
        ]
    
    def ClearSearchHistory(self) -> bool:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM search_history")
        conn.commit()
        conn.close()
        return True
    
    def GetFavoritesCount(self) -> int:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM favorites")
        count = c.fetchone()[0]
        conn.close()
        return count


_favorites_manager: Optional[FavoritesManager] = None


def GetFavoritesManager() -> FavoritesManager:
    global _favorites_manager
    if _favorites_manager is None:
        _favorites_manager = FavoritesManager()
    return _favorites_manager
