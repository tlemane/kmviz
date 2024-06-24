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
