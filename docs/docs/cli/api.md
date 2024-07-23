# :fontawesome-solid-terminal: kmviz api

The `kmviz api` command group contains utilities to request the **kmviz** API without making manuel HTTP requests.

<!-- termynal -->
```
$ python -m kmviz api --help

Usage: python -m kmviz api [OPTIONS] COMMAND [ARGS]...

  Query kmviz REST API

Options:
  -u, --url <str>               Host  [default: http://localhost]
  -p, --port <int>              Port
  -a, --auth <user>:<password>  HTTP BasicAuth credentials
  --help                        Show this message and exit.

Commands:
  infos     Get databases information
  metadata  Make queries and get results as a tsv dataframe
  query     Make queries and get results as a json session file, viewable...
```

=== "kmviz api infos"
    `kmviz api infos` retrieves instance information in `JSON` format. This information includes registered `databases` and their options, making it useful for constructing API requests.
    <!-- termynal -->
    ```
    $ python -m kmviz api infos --help

    Usage: python -m kmviz api infos [OPTIONS]

      Get databases information

    Options:
      -r, --route <str>    Route  [default: /api]
      -o, --output <path>  Output file  [default: stdout]
      --help               Show this message and exit.
    ```

=== "kmviz api metadata"
    `kmviz api metadata` command allows you to query a `database` and obtain a zip archive of results, with one `TSV` file per query sequence. Note that the archive name is a `session-id`, which can be used to reload the result on the interface associated with the API endpoint, if it exists.
    <!-- termynal -->
    ```
    $ python -m kmviz api metadata --help

    Usage: python -m kmviz api metadata [OPTIONS]

      Make queries and get results as a tsv dataframe

    Options:
      -r, --route <str>             Query route  [default: /api/query]
      -o, --output <dir>            Output directory  [default: .]
      -d, --database <str>          Database to query  [required]
      -x, --opt <opt_name> <value>  Database option, -x <opt_name> <value>
      -f, --fastx <path>            Path to fastx query file  [required]
      --help                        Show this message and exit.

    ```

=== "kmviz api query"
    `kmviz api query` allows you to query an instance to obtain a `JSON` session file, which can then be reloaded into a kmviz instance in [`session mode`](../interface/session.md).
    <!-- termynal -->
    ```
    $ python -m kmviz api query --help

    Usage: python -m kmviz api query [OPTIONS]

      Make queries and get results as a json session file, viewable using a local
      kmviz instance. See kmviz app start session

    Options:
      -r, --route <str>               Query route  [default: /api/query]
      -o, --output <path>             Output file  [default: stdout]
      -d, --database <str>            Database to query  [required]
      -x, --opt <db_name> <opt_name> <value>
                                      Database options
      -f, --fastx <path>              Path to fastx query file  [required]
      --help                          Show this message and exit.
    ```
