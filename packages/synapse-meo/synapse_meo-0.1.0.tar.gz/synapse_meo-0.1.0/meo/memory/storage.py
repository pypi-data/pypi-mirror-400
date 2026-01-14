from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import json
import os
import sqlite3
from pathlib import Path


class StorageBackend(ABC):
    @abstractmethod
    def save(self, key: str, data: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def load_all(self, prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        pass
    
    @abstractmethod
    def clear(self) -> None:
        pass


class JSONLStorage(StorageBackend):
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._ensure_directory()
    
    def _ensure_directory(self) -> None:
        directory = os.path.dirname(self.filepath)
        if directory:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def save(self, key: str, data: Dict[str, Any]) -> None:
        self._ensure_directory()
        
        record = {"_key": key, **data}
        
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        if not os.path.exists(self.filepath):
            return None
        
        with open(self.filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    if record.get("_key") == key:
                        record.pop("_key", None)
                        return record
        
        return None
    
    def load_all(self, prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        if not os.path.exists(self.filepath):
            return []
        
        results = []
        with open(self.filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    key = record.get("_key", "")
                    
                    if prefix is None or key.startswith(prefix):
                        record.pop("_key", None)
                        results.append(record)
        
        return results
    
    def delete(self, key: str) -> None:
        if not os.path.exists(self.filepath):
            return
        
        temp_filepath = self.filepath + ".tmp"
        
        with open(self.filepath, "r", encoding="utf-8") as f_in:
            with open(temp_filepath, "w", encoding="utf-8") as f_out:
                for line in f_in:
                    if line.strip():
                        record = json.loads(line)
                        if record.get("_key") != key:
                            f_out.write(line)
        
        os.replace(temp_filepath, self.filepath)
    
    def clear(self) -> None:
        if os.path.exists(self.filepath):
            os.remove(self.filepath)


class SQLiteStorage(StorageBackend):
    def __init__(self, db_path: str, table_name: str = "meo_storage"):
        self.db_path = db_path
        self.table_name = table_name
        self._ensure_directory()
        self._initialize_db()
    
    def _ensure_directory(self) -> None:
        directory = os.path.dirname(self.db_path)
        if directory:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def _initialize_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    key TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def save(self, key: str, data: Dict[str, Any]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"INSERT OR REPLACE INTO {self.table_name} (key, data) VALUES (?, ?)",
                (key, json.dumps(data)),
            )
            conn.commit()
    
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT data FROM {self.table_name} WHERE key = ?",
                (key,),
            )
            row = cursor.fetchone()
            
            if row:
                return json.loads(row[0])
            return None
    
    def load_all(self, prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if prefix:
                cursor.execute(
                    f"SELECT data FROM {self.table_name} WHERE key LIKE ?",
                    (f"{prefix}%",),
                )
            else:
                cursor.execute(f"SELECT data FROM {self.table_name}")
            
            rows = cursor.fetchall()
            return [json.loads(row[0]) for row in rows]
    
    def delete(self, key: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {self.table_name} WHERE key = ?", (key,))
            conn.commit()
    
    def clear(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {self.table_name}")
            conn.commit()
