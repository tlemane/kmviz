# Configuration

**kmviz** can be configured using a [`yaml`](https://yaml.org/) or [`toml`](https://toml.io/en/) configuration file. This documentation uses `yaml` as examples but `toml` version is available [here](https://github.com/tlemane/kmviz/tests/small_example/config.toml).

The **kmviz** configuration is divided into 3 main sections: `databases`, `cache` and `auth` (optional), described separately here for clarity, but in practice the configuration must be kept within a single `yaml`/`toml` file.

An optional section can also be used to describe visualization presets, see [Presets](#presets-section).

## Databases section

```yaml title="config.yaml (databases section)"
databases:
  - ExampleDB:
      type: "kmindex-server"
      params:
        url: "127.0.0.1"
        port: 8080
      metadata:
        type: "tsv"
        params:
          path: "./metadata.tsv"
          sep: "\t"
          idx: "Sample"
          geodata:
            latitude: "Lat"
            longitude: "Long"
```

## Cache section

For local instances, cache configuration is not a critical point. The example below will work in many cases.

:warning: For multi-user instances, a particular attention is recommended, see [Advanced/Deployment](deploy.md).

```yaml
cache:
  manager:
    type: "disk"
    params:
      directory: "./kmviz_manager_cache"

  result:
    params:
      directory: "./kmviz_result_cache"
      size_limit: 20000000000

  backend: "./kmviz_backend"
```

## Authentication section

At the moment, **kmviz** has limited authentication support with only [HTTP BasicAuth](https://datatracker.ietf.org/doc/html/rfc7617). Crendentials can be specified directly in the configuration file, or retrieved through the system keyring service. See [jaraco/keyring](https://github.com/jaraco/keyring) for the list of supported keyring backends.

Note that authentication section is optional.


```yaml title="Inline"
auth:
  username: "password"
  username_2: "password_2"
```

```yaml title="Keyring"
auth:
  - username
  - username_2
```

## Presets section

:construction: