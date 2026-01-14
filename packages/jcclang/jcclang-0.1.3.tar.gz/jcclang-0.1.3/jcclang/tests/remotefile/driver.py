import os

import requests


class Driver:
    def open(self, url: str, mode="rb"):
        raise NotImplementedError

    def read(self, url: str, offset: int, size: int = -1) -> bytes:
        raise NotImplementedError

    def size(self, url: str) -> int:
        raise NotImplementedError

    def close(self, url: str):
        raise NotImplementedError


class LocalDriver(Driver):
    def __init__(self):
        self.handles = {}

    def open(self, url, mode="rb"):
        path = url.replace("file://", "")
        self.handles[url] = open(path, mode)

    def read(self, url, offset, size=-1):
        f = self.handles[url]
        f.seek(offset)
        return f.read(size)

    def size(self, url):
        path = url.replace("file://", "")
        return os.path.getsize(path)

    def close(self, url):
        self.handles[url].close()
        del self.handles[url]


class HTTPRangeDriver(Driver):
    def __init__(self):
        self.sessions = {}

    def open(self, url, mode="rb"):
        self.sessions[url] = requests.Session()

    def read(self, url, offset, size=-1):
        headers = {"Range": f"bytes={offset}-"}
        if size > 0:
            headers["Range"] = f"bytes={offset}-{offset + size - 1}"
        r = self.sessions[url].get(url, headers=headers, stream=True)
        r.raise_for_status()
        return r.content

    def size(self, url):
        r = requests.head(url)
        return int(r.headers.get("Content-Length", -1))

    def close(self, url):
        self.sessions[url].close()
        del self.sessions[url]


class RemoteFile:
    def __init__(self, url: str, driver: Driver):
        self.url = url
        self.driver = driver
        self.driver.open(url)
        self.position = 0

    def read(self, size: int = -1) -> bytes:
        data = self.driver.read(self.url, self.position, size)
        self.position += len(data)
        return data

    def seek(self, offset: int, whence: int = 0):
        if whence == 0:
            self.position = offset
        elif whence == 1:
            self.position += offset
        elif whence == 2:
            size = self.size()
            self.position = size + offset

    def tell(self) -> int:
        return self.position

    def size(self) -> int:
        return self.driver.size(self.url)

    def close(self):
        self.driver.close(self.url)
