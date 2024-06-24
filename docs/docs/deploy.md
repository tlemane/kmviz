# Deployment

While the default devlopment server ([flask](https://flask.palletsprojects.com/en/3.0.x/)) is fine for running **kmviz** locally, it is recommended to use a production-ready server to deploy an instance that can be accessed by several users.

The following WSGI servers have been tested:

* [gunicorn](https://gunicorn.org/)
* [fastwsgi](https://github.com/jamesroberts/fastwsgi)
* [socketify](https://docs.socketify.dev/)

We provide a docker image, `tlemane/kmviz`, to easily deploy `kmviz` using `gunicorn`.

## Configuration

When executed with a WSGI server, the path to the configuration file is given by the `KMVIZ_CONF` environment variable.

### Cache and backends

:construction: WIP :construction:

## Deploy

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
