#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import annotations

__all__ = ['CaptchaStorage', 'MemoryCaptchaStorage', 'SqliteCaptchaStorage']

# Import modules
from threading import Lock
from sqlite3 import connect
from typing import Protocol, Set
from dataclasses import dataclass
from datetime import datetime, timezone


class CaptchaStorage(Protocol):
    def is_verified(self, user_id: int) -> bool: ...

    def mark_verified(self, user_id: int) -> None: ...

    def reset(self, user_id: int) -> None: ...


@dataclass
class MemoryCaptchaStorage:
    _verified: Set[int]

    def __init__(self) -> None:
        self._verified = set()

    def is_verified(self, user_id: int) -> bool:
        return user_id in self._verified

    def mark_verified(self, user_id: int) -> None:
        self._verified.add(user_id)

    def reset(self, user_id: int) -> None:
        self._verified.discard(user_id)


class SqliteCaptchaStorage:
    def __init__(self, db_path: str = "aiocaptcha.sqlite3") -> None:
        self._db_path = db_path
        self._lock = Lock()
        self._conn = connect(self._db_path, check_same_thread=False)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS aiocaptcha_verified_users (
                user_id INTEGER PRIMARY KEY,
                verified_at TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    def is_verified(self, user_id: int) -> bool:
        with self._lock:
            cur = self._conn.execute(
                "SELECT 1 FROM aiocaptcha_verified_users WHERE user_id = ? LIMIT 1",
                (user_id,),
            )
            return cur.fetchone() is not None

    def mark_verified(self, user_id: int) -> None:
        verified_at = datetime.now(timezone.utc).isoformat()
        with self._lock:
            self._conn.execute(
                "INSERT OR REPLACE INTO aiocaptcha_verified_users (user_id, verified_at) VALUES (?, ?)",
                (user_id, verified_at),
            )
            self._conn.commit()

    def reset(self, user_id: int) -> None:
        with self._lock:
            self._conn.execute(
                "DELETE FROM aiocaptcha_verified_users WHERE user_id = ?",
                (user_id,),
            )
            self._conn.commit()

    def close(self) -> None:
        with self._lock:
            self._conn.close()
