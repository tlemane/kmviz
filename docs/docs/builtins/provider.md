# Provider

## `kmindex server`

|Parameter|Description|Default|Required|
|---|---|---|---|
|url|Index url|-|:white_check_mark:|
|port|Port|-|:white_check_mark:|

<div class="grid" markdown>

```yaml title="kmindex_server_ex.yaml"
Example:
  type: "kmindex-server"
  params:
    url: "127.0.0.1"
    port: 8080
```

```toml title="kmindex_server_ex.toml"
[databases.Example]
type = "kmindex-server"
[databases.Example.params]
url = "127.0.0.1"
port = 8080
```

</div>