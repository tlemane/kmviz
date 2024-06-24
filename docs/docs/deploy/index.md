# Deployment

While the default devlopment server ([flask](https://flask.palletsprojects.com/en/3.0.x/)) is fine for running **kmviz** locally, it is recommended to use a production-ready server to deploy an instance that can be accessed by several users.

The following WSGI servers have been tested:

* [gunicorn](https://gunicorn.org/)
* [fastwsgi](https://github.com/jamesroberts/fastwsgi)
* [socketify](https://docs.socketify.dev/)

!!! Note
    When executed with a WSGI server, the path to the configuration file is given by the `KMVIZ_CONF` environment variable.

We provide a docker image, [:fontawesome-brands-docker: tlemane/kmviz](https://hub.docker.com/r/tlemane/kmviz), to easily deploy `kmviz` using `gunicorn` (see [Docker](docker.md)).

See [Docker compose](compose.md) for a complete deployment example including:

* A sequence index, using **kmindex**.
* A metadata db, using **MySQL**.
* A **kmviz** instance
