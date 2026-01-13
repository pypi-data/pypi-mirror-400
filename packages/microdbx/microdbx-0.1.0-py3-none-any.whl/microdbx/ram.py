import time

class RAMDB:
    def __init__(self, max_size=255):
        self._data={}
        self.max_size=max_size

    def _now(self) -> float:
        return time.time()

    def _is_expired(self, meta) -> bool:
        expire_at=meta["expire_at"]
        return expire_at is not None and expire_at <= self._now()

    def _cleanup_expired(self) -> None:
        now=self._now()
        to_delete=[]
        for k, meta in self._data.items():
            if meta["expire_at"] is not None and meta["expire_at"] <= now:
                to_delete.append(k)

        for k in to_delete:
            del self._data[k]

    def _ensure_size(self) -> None:
        if len(self._data) <= self.max_size:
            return

        items = sorted(
            self._data.items(),
            key=lambda x: x[1]["created_at"]
        )

        while len(items) > self.max_size:
            k, _ = items.pop(0)
            self._data.pop(k, None)

    def set(self, key:str, value:str, ttl=None) -> None:
        self._cleanup_expired()

        expire_at = None
        if ttl is not None:
            expire_at = self._now() + ttl

        self._data[key]={
            "value": value,
            "expire_at": expire_at,
            "created_at": self._now()
        }

        self._ensure_size()

    def get(self, key:str, default=None):
        meta=self._data.get(key)
        if not meta:
            return default

        if self._is_expired(meta):
            del self._data[key]
            return default

        return meta["value"]

    def delete(self, key:str) -> None:
        if key is self._data:
            del self._data[key]

    def exists(self, key:str) -> bool:
        return self.get(key, None) is not None

    def clear(self) -> None:
        self._data.clear()

    def size(self) -> int:
        self._cleanup_expired()
        return len(self._data)
