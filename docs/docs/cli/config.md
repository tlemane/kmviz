# :fontawesome-solid-terminal: kmviz config

<!-- termynal -->

```
$ python -m kmviz config --help

Usage: python -m kmviz config [OPTIONS] COMMAND [ARGS]...

  Configuration helpers

Options:
  --help  Show this message and exit.

Commands:
  check     Valid configuration file.
  schema    Make JSON schema
  template  Make configuration templates
```

=== "kmviz config check"
    `kmviz config check` allows you to validate a configuration file (`JSON`, `TOML` or `YAML`) for syntax, required fields, variable types, etc. With the `--with-init` flag, it also attempts an initialization, such as connecting to databases, loading plugins, etc.

    <!-- termynal -->
    ```
    $ python -m kmviz config check --help

    Usage: python -m kmviz config check [OPTIONS]

      Valid configuration file. With --with-init, the validation process also
      tries to init the app, i.e. connect to databases, load plugins, etc

    Options:
      -c, --config <path>  Path to config file  [required]
      -w, --with-init      Try to init
      -d, --details        Show schema on error
      --help               Show this message and exit.
    ```

=== "kmviz config schema"
    `kmviz config schema` command dumps a [JSON validation schema](https://json-schema.org/) for the configuration.
    <!-- termynal -->
    ```
    $ python -m kmviz config schema --help

    Usage: python -m kmviz config schema [OPTIONS]

      Make JSON schema

    Options:
      -o, --output <path>  Output file prefix  [default: stdout]
      --help               Show this message and exit.
    ```

=== "kmviz config template"
    `kmviz config template` command allows to generate complete or partial configuration file templates in all supported formats, such as `JSON`, `TOML`, and `YAML`.
    <!-- termynal -->
    ```
    $ python -m kmviz config template --help

    Usage: python -m kmviz config template [OPTIONS]

      Make configuration templates

    Options:
      -f, --fmt [toml|yaml|json]      File format  [default: yaml]
      -s, --section [all|databases|input|api|auth|defaults|plugins|cache|html]
                                      [default: all]
      -o, --output <path>             Output file prefix  [default: stdout]
      --help                          Show this message and exit.
    ```
