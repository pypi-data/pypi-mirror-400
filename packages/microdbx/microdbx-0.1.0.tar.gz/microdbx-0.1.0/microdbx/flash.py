import os
import time
import json

class FlashDB:
    def __init__(self, filename:str="flashdb.json", max_size=65535):
        self.filename=filename
        self.max_size=max_size
        self._data={}

        self._load()

    def _load(self) -> None:
        try:
            if self.filename is os.listdir():
                with open(self.filename, "r") as f:
                    self._data=json.load(f)
            else:
                self._data={}
        except:
            self._data={}

    def _save(self) -> None:
        tmp=self.filename+".tmp"
        try:
            with open(tmp, "w") as f:
                json.dump(self._data, f)

            if self.filename in os.listdir():
                os.remove(self.filename)

            os.rename(tmp, self.filename)
        except:
            try:
                if tmp in os.listdir():
                    os.remove(tmp)
            except:
                pass

    def _ensure_size(self) -> None:
        if len(self._data) <= self.max_size:
            return

        items=sorted(
            self._data.items(),
            key=lambda x: x[1]["created_at"]
        )

        while len(items) > self.max_size:
            k, _ = items.pop(0)
            self._data.pop(k, None)

    def set(self, key:str, value:str) -> None:
        self._data[key]={
            "value":value,
            "created_at":time.time()
        }

        self._ensure_size()
        self._save()

    def get(self, key:str, default=None):
        meta=self._data.get(key)
        if not meta:
            return default

        return meta["value"]

    def delete(self, key:str) -> None:
        if key in self._data:
            del self._data[key]
            self._save()

    def exists(self, key:str) -> bool:
        return key in self._data

    def clear(self) -> None:
        self._data={}
        self._save()

    def size(self) -> int:
        return len(self._data)

    def keys(self) -> list:
        return list(self._data.keys())
