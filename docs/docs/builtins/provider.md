# Provider

## `kmindex server (kmindex >= v0.5.3)`

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

### User options

- `z`: See [kmindex documentation](https://tlemane.github.io/kmindex).
- `coverage`: The min ratio of shared *k*-mer to consider a match between a query and a sample.