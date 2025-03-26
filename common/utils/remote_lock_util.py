from typing import Optional

from django.conf import settings
from django.core.cache import cache

from redlock import Redlock

redlock = Redlock(settings.REDLOCK)


def acquire(key: str, expire_time: Optional[int]) -> bool:
    acquired_lock = redlock.lock(key, 15000)
    if not acquired_lock:
        return False

    is_running = cache.get(f"{key}_running")
    if is_running == '1':
        redlock.unlock(acquired_lock)
        return False

    # set running flag and release lock
    cache.set(f"{key}_running", '1', expire_time)
    redlock.unlock(acquired_lock)
    return True


def release(key: str):
    cache.delete(f"{key}_running")


def set_key(key: str, expire_time: int):
    cache.set(f"{key}_running", '1', expire_time)


def get_key(key: str):
    return cache.get(f"{key}_running")


class AcquireRemoteLock:
    def __init__(self, key: str, expire_time: int):
        self.key = key
        self.expire_time = expire_time
        self.acquired_lock = None

    def __enter__(self) -> bool:
        self.acquired_lock = redlock.lock(self.key, 15000)
        if not self.acquired_lock:
            return False

        is_running = cache.get(f"{self.key}_running")
        if is_running == '1':
            redlock.unlock(self.acquired_lock)
            return False

        # set running flag and release lock
        cache.set(f"{self.key}_running", '1', self.expire_time)
        redlock.unlock(self.acquired_lock)
        return True

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.acquired_lock:
            cache.set(f"{self.key}_running", '0', self.expire_time)
