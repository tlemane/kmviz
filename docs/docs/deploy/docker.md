# Docker

<details>
<summary>Dockerfile</summary>
```docker
FROM python

WORKDIR /home

RUN pip install kmviz gunicorn
ENV KMVIZ_CONF=/home/config.toml

ENTRYPOINT ["kmviz", "app", "deploy"]
CMD ["-u 0.0.0.0", "-p 8000"]
```

</details>

```bash title="Start the service using docker"
docker pull tlemane/kmviz
docker run -d --network="host" -p .:/home/ -w 1 -u 0.0.0.0 -p 8000
```

* Docker Options
    * `--network="host"`: Use the host network
    * `-p .:/home/`: Mount `.` at `/home/`
    * `-d`: Detach the container

* Server Options (See [`kmviz app deploy`](../cli/app.md))
    * `-w`: The number of workers
    * `-u`: Host
    * `-p`: Port

By default, `KMVIZ_CONF` is set to `/home/config.toml`. To use another filename, use `docker run --env KMVIZ_CONF=/home/my_config.yaml ...`.

## About cache

3 caching systems are used in **kmviz**:

* `manager`: For [Background callback](https://dash.plotly.com/background-callbacks) support
* `serverside`: For [Serverside output](https://www.dash-extensions.com/transforms/serverside_output_transform) support
* `result`: Store user sessions

### `serverside` and `result` configuration

**Available backends**

- `disk`, based on [cachelib.FileSystemCache](https://cachelib.readthedocs.io/en/stable/file/#cachelib.file.FileSystemCache)
- `redis`, based on [cachelib.RedisCache](https://cachelib.readthedocs.io/en/stable/redis/#cachelib.redis.RedisCache)


<div class="grid" markdown>
```toml title="Disk"
[cache.result]
type = "disk"
params.cache_dir = "result_cache"
params.threshold = 0
params.default_timeout = 1209600
```

```toml title="Redis"
[cache.result]
type = "redis"
params.host = "localhost"
params.port = 6379
params.db = 1
params.default_timeout = 86400
```
</div>

!!! Note
    `redis` is recommended for both `serverside` and `result` when deploying multi-user instances.

!!! Warning "About timeout"
    * `result`: The `default_timeout` field corresponds the time during which a user can access a result without recomputing the query.
    * `serverside`: The cache should always return and value, *i.e.* keys should not expire during a user session. Use a significant value, *e.g.* 24 hours.

### `manager` configuration

**Available backends**

* `disk`, based on [DiskCache.Cache](https://grantjenks.com/docs/diskcache/api.html#diskcache.Cache)
* `fanout`, based on [DiskCache.FanoutCache](https://grantjenks.com/docs/diskcache/api.html#diskcache.FanoutCache) (:construction: coming soon)
* `celery`, based on [Celery](https://docs.celeryq.dev/en/stable/reference/celery.html#celery.Celery) (:construction: coming soon)

```toml title="Disk"
[cache.manager]
type = "disk"
params.directory = ".results/kmviz_manager_cache"
```

### Complete example

```toml title="config.toml"
[cache]

[cache.serverside]
type = "redis"
[cache.serverside.params]
host = "localhost"
port = 6379
db = 0
default_timeout = 86400

[cache.manager]
type = "disk"
params.directory = "./kmviz_manager_cache"

[cache.result]
type = "disk"
[cache.result.params]
cache_dir = "./kmviz_result_cache"
threshold = 0
default_timeout = 1209600
```
