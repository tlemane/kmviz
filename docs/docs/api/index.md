# API

A **kmviz** instance can  host a REST API that allows querying the underlying databases. When enabled, the available features are:

- [Information query](./index.md), which return info about the instance: list of databases, parameters, etc.
- [Metadata query](./metadata.md), which return a TSV file per query containing the hits and associated metadata.
- [Session query](./session.md), which return a JSON file that can be explored in any other **kmviz** instance running in [session mode]().

Note that **kmviz** provides CLI tools to simplify the execution of these queries, avoiding the need to make raw HTTP requests.

=== "kmviz api"
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