# Deployment

While the default development server ([flask](https://flask.palletsprojects.com/en/3.0.x/)) is fine for running **kmviz** locally, it is recommended to use a production-ready server to deploy an instance that can be accessed by several users.

**kmviz** offers a small CLI tool to deploy an instance using [gunicorn](https://gunicorn.org/).

<!-- termynal -->
```
$ python -m kmviz app deploy --help

Usage: python -m kmviz app deploy [OPTIONS]

    Deployment with gunicorn (recommended for multi-user instances)

Options:
    -m, --mode <str>               Mode, 'db' or 'api'  [default: db]
    -u, --url <str>                Host  [default: localhost]
    -p, --port <int>               Port  [default: 8000]
    -w, --workers <int>            Number of workers  [default: 25]
    -r, --reload-extra-file <str>  Reload when files change
    -e, --extra <option> <value>   Extra gunicorn options
    --help                         Show this message and exit.
```

Ex: `python -m kmviz app -c config.toml deploy -u 0.0.0.0 --port 8080 -w 8`

We provide a docker image, [:fontawesome-brands-docker: tlemane/kmviz](https://hub.docker.com/r/tlemane/kmviz), to easily deploy `kmviz` using `gunicorn` (see [Docker](docker.md)).

See [Docker compose](compose.md) for a complete deployment example including:

* A sequence index, using **kmindex**.
* A metadata db, using **MySQL**.
* A **kmviz** instance

---

## Deploy with another server

The following WSGI servers have been tested:

* [gunicorn](https://gunicorn.org/)
* [fastwsgi](https://github.com/jamesroberts/fastwsgi)
* [socketify](https://docs.socketify.dev/)


!!! Note
    The WSGI application is located at `kmviz/app.py` and the variable named is `app`. For example with `gunicorn`: `gunicorn -w 1 kmviz.app:app`

!!! Note
    When executed with a WSGI server, the path to the configuration file is given by the `KMVIZ_CONF` environment variable.

---

