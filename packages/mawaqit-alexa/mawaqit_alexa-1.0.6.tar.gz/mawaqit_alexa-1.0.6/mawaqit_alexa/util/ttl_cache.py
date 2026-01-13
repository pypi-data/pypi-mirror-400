import sqlite3
import time
import functools
import pickle
import hashlib
import tempfile
import random
from pathlib import Path
from typing import Any, Optional


# --- Internal Backend (The heavy lifter) ---

class _CacheBackend:
    """
    Handles the actual File I/O and SQLite operations.
    This is instantiated only when we have a valid path.
    """

    def __init__(self, cache_dir: Path, db_name: str = "cache_metadata.db"):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / db_name
        self._conn = None  # Lazy connection
        self._init_db()

    def _get_conn(self):
        """Maintains a persistent connection for performance."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.execute("PRAGMA journal_mode=WAL;")  # Better concurrency
            self._conn.execute("PRAGMA synchronous=NORMAL;")  # Faster writes
        return self._conn

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                         CREATE TABLE IF NOT EXISTS cache_index
                         (
                             key        TEXT PRIMARY KEY,
                             filename   TEXT NOT NULL,
                             expires_at REAL NOT NULL
                         )
                         """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_expires ON cache_index (expires_at)")

    def close(self):
        """Safely close connection if we switch directories."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def get_key(self, func_name: str, args, kwargs) -> str:
        # Include function name in hash to prevent collisions between different funcs with same args
        payload = pickle.dumps((func_name, args, sorted(kwargs.items())))
        return hashlib.sha256(payload).hexdigest()

    def get(self, key: str) -> Any:
        conn = self._get_conn()
        cursor = conn.execute("SELECT filename, expires_at FROM cache_index WHERE key = ?", (key,))
        row = cursor.fetchone()

        if not row:
            return None

        filename, expires_at = row

        if time.time() > expires_at:
            self.delete(key, filename)  # Lazy expiry
            return None

        try:
            with open(self.cache_dir / filename, "rb") as f:
                return pickle.load(f)
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            self.delete(key, filename)
            return None

    def set(self, key: str, value: Any, ttl_seconds: int):
        filename = f"{key}.pkl"
        expires_at = time.time() + ttl_seconds

        # Atomic-ish write: write to temp file then rename?
        # For simplicity in this example, direct write is usually fine for single-process.
        with open(self.cache_dir / filename, "wb") as f:
            pickle.dump(value, f)

        conn = self._get_conn()
        conn.execute("""
            INSERT OR REPLACE INTO cache_index (key, filename, expires_at)
            VALUES (?, ?, ?)
        """, (key, filename, expires_at))
        conn.commit()

    def delete(self, key: str, filename: str):
        try:
            (self.cache_dir / filename).unlink(missing_ok=True)
        except OSError:
            pass
        conn = self._get_conn()
        conn.execute("DELETE FROM cache_index WHERE key = ?", (key,))
        conn.commit()

    def prune_expired(self):
        now = time.time()
        conn = self._get_conn()
        cursor = conn.execute("SELECT key, filename FROM cache_index WHERE expires_at < ?", (now,))
        rows = cursor.fetchall()

        if rows:
            for key, filename in rows:
                try:
                    (self.cache_dir / filename).unlink(missing_ok=True)
                except OSError:
                    pass
            conn.execute("DELETE FROM cache_index WHERE expires_at < ?", (now,))
            conn.commit()


# --- Global State Manager ---

class CacheManager:
    _backend: Optional[_CacheBackend] = None

    @classmethod
    def configure(cls, path: str):
        """
        User calls this to set the folder.
        If a backend already exists, we close it and start a new one.
        """
        if cls._backend:
            cls._backend.close()

        print(f"🔧 Configuring Cache at: {path}")
        cls._backend = _CacheBackend(Path(path))

    @classmethod
    def get_backend(cls) -> _CacheBackend:
        """
        Returns the active backend.
        If not configured, creates a default one in /tmp.
        """
        if cls._backend is None:
            # Default fallback: System Temp Dir
            default_path = Path(tempfile.gettempdir()) / "myapp_default_cache"
            cls.configure(str(default_path))
        return cls._backend


# --- The Public Decorator ---

def persistent_ttl_cache(seconds: int, logger_callback=None):
    """
    Decorator that stores data in the globally configured cache folder.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Get the global backend (Lazily)
            backend = CacheManager.get_backend()

            # 2. Generate Key
            key = backend.get_key(func.__name__, args, kwargs)

            # 3. Check Cache
            cached_val = backend.get(key)
            if cached_val is not None:
                if logger_callback: logger_callback(f"⚡ [Hit] {func.__name__}")
                return cached_val

            # 4. Run Function
            if logger_callback: logger_callback(f"🐢 [Miss] {func.__name__}")
            result = func(*args, **kwargs)

            # 5. Store Result
            backend.set(key, result, seconds)

            # 6. Cleanup Chance (1%)
            if random.random() < 0.01:
                backend.prune_expired()

            return result

        return wrapper

    return decorator


# --- Helper for the user ---
def configure_cache(path: str):
    """Public API to set the cache location."""
    CacheManager.configure(path)
