# Docker

```bash title="Start the service using docker"
docker pull tlemane/kmviz
docker run -d --network="host" -p .:/home/ -w 4 -b 0.0.0.0:8000
```

* Docker Options
    * `--network="host"`: Use the host network
    * `-p .:/home/`: Mount `.` at `/home/`
    * `-d`: Detach the container
* Server Options
    * `-w`: The number of workers
    * `-b`: Host and port, `<url>:<port>`

By default, `KMVIZ_CONF` is set to `/home/config.toml`. To use another filename, use `docker run --env KMVIZ_CONF=/home/my_config.yaml ...`.

## About cache and backends

:construction: WIP :construction:
