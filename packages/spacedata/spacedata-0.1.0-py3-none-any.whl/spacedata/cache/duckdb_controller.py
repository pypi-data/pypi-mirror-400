import datetime
import json

import duckdb

from spacedata.cache.base import BaseCacheController, CacheEntry
from spacedata.settings import SpaceDataSettings


class DuckDBCacheController(BaseCacheController):
    def __init__(self, settings: SpaceDataSettings) -> None:
        self.settings = settings

        with self._get_conn() as conn:
            conn.sql(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    data JSON,
                    created_at TIMESTAMP DEFAULT now(),
                    expires_at TIMESTAMP
                );
                """
            )

    def _get_conn(self):
        return duckdb.connect(self.settings.duckdb_url)

    def get(self, key: str) -> CacheEntry | None:
        with self._get_conn() as conn:
            row = conn.execute(
                """
                SELECT data, created_at, expires_at
                FROM cache
                WHERE key = ?
                    AND (expires_at IS NULL OR expires_at > now())
                """,
                [key],
            ).fetchone()

            if row is None:
                return None

            data, created_at, expires_at = row
            data = json.loads(data)
            return CacheEntry(
                key=key, created_at=created_at, data=data, expires_at=expires_at
            )

    def set(self, key: str, data: dict | list[dict], ttl: int | None = None) -> bool:
        expires_at = None
        if ttl is not None:
            expires_at = datetime.datetime.now() + datetime.timedelta(seconds=ttl)

        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO cache (key, data, expires_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key)
                DO UPDATE SET
                    data = excluded.data,
                    expires_at = excluded.expires_at,
                    created_at = now()
                """,
                [key, json.dumps(data), expires_at],
            )

        return True
