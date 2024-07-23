# :fontawesome-solid-terminal: kmviz app

<!-- termynal -->

```
$ python -m kmviz app --help

Usage: python -m kmviz app [OPTIONS] COMMAND [ARGS]...

  Start kmviz

Options:
  -c, --config <path>  Path to config file
  --help               Show this message and exit.

Commands:
  deploy  Deployment with gunicorn (recommended for multi-user instances)
  start   Start with flask server (recommenced for single users)
```

=== "kmviz app start"
    `kmviz app start` runs an instance with [Flask](https://flask.palletsprojects.com/) and supports all modes. It is recommended for single users.
    <!-- termynal -->
    ```
    $ python -m kmviz app start --help

    Usage: python -m kmviz app start [OPTIONS] [[db|session|plot|api]]

      Start with flask server (recommenced for single users)

      Mode:
        - db (default)
        - session: Session mode, see https://tlemane/github.io/kmviz/)
        - plot: Plot mode, see https://tlemane/github.io/kmviz/)
        - api: Only start the kmviz REST API (see https://tlemane/github.io/kmviz/)

    Options:
      -u, --url <str>   url  [default: localhost]
      -p, --port <int>  port  [default: 8050]
      -d, --debug
      --help            Show this message and exit.
    ```

=== "kmviz app deploy"
    `kmviz app deploy` runs an instance on a production-ready [WSGI server](https://wsgi.readthedocs.io/en/latest/), i.e. [Gunircorn](https://gunicorn.org/). It supports only `db` and `api` modes. It is recommended for deploying instances.
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