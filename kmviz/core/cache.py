from dash import DiskcacheManager, CeleryManager

def callback_manager(params: dict):
    if params["type"] == "disk":
        return disk_callback_manager(params["params"])
    else:
        return celery_callback_manager(params["params"])

def disk_callback_manager(params) -> DiskcacheManager:
    import diskcache
    cache = diskcache.Cache(**params)
    return DiskcacheManager(cache)

def celery_callback_manager(params) -> CeleryManager:
    from celery import Celery
    app = Celery("kmviz", **params)
    return CeleryManager(app)

def result_cache_manager(params: dict):
    import diskcache
    cache = diskcache.Cache(**params)
    return cache
