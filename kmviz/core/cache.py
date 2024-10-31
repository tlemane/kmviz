def make_server_cache_manager(params: dict):
    if params["type"] == "disk":
        from dash_extensions.enrich import FileSystemBackend
        return FileSystemBackend(**params["params"])
    elif params["type"] == "redis":
        from dash_extensions.enrich import RedisBackend
        return RedisBackend(**params["params"])

def make_result_cache_manager(params: dict):
    if params["type"] == "disk":
        from cachelib.file import FileSystemCache
        return FileSystemCache(**params["params"])
    elif params["type"] == "redis":
        from cachelib.redis import RedisCache
        return RedisCache(**params["params"])

def make_callback_cache_manager(params: dict):
    from dash import DiskcacheManager, CeleryManager
    if params["type"] == "disk":
        import diskcache
        return DiskcacheManager(diskcache.Cache(**params["params"]))
    elif params["type"] == "celery":
        from celery import Celery
        return CeleryManager(Celery(**params["params"]))

from kmviz.core import KmVizError

class KmvizResultCache:
    def __init__(self, backend):
        self._backend = backend

    def get(self, uid: str):
        res = self._backend.get(uid)
        if res is None:
            raise KmVizError(f"'{uid}' not in cache")
        return res

    def put(self, uid: str, value):
        self._backend.set(uid, value)

    def inc(self, uid: str, delta):
        return self._backend.inc(uid, delta)

    def dec(self, uid: str, delta):
        return self._backend.dec(uid, delta)

    def has(self, uid: str):
        return self._backend.has(uid)

    def set(self, uid: str, value):
        self._backend.set(uid, value)

    @property
    def back(self):
        return self._backend