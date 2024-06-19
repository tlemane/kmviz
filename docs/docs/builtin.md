---
hide:
 - navigation
---

## Provider

### `kmindex-server`

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

## MetaDB

### `sqlite`

|Parameter|Description|Default|Required|
|---|---|---|---|
|path|Path to the `sqlite` file |-|:white_check_mark:|
|table|The name of table|-|:white_check_mark:|
|idx|The name of the column containing identifiers|-|:white_check_mark:|
|geodata|The name of the columns containing geographical data, if applicable|-|:x:|

<div class="grid" markdown>

```yaml title="tsv_ex.yaml"
metadata:
  type: "sqlite"
  params:
    path: "./metadata.sqlite"
    table: "table"
    idx: "Sample"
    geodata:
      latitude: "Lat"
      longitude: "Long"
```

```toml title="tsv_ex.toml"
[databases.Example.metadata]
type = "sqlite"
[databases.Example.metadata.params]
path = "./metadata.sqlite"
table = "table"
idx = "Sample"
geodata = { latitude = "Lat", longitude = "Long"}
```
</div>


### `tsv`

|Parameter|Description|Default|Required|
|---|---|---|---|
|path|Path to the `tsv` file |-|:white_check_mark:|
|sep|Separator|'\t'|:x:|
|idx|The name of the column containing identifiers|-|:white_check_mark:|
|geodata|The name of the columns containing geographical data, if applicable|-|:x:|

<div class="grid" markdown>

```yaml title="tsv_ex.yaml"
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

```toml title="tsv_ex.toml"
[databases.Example.metadata]
type = "tsv"
[databases.Example.metadata.params]
path = "./metadata.tsv"
sep = "\t"
idx = "Sample"
geodata = { latitude = "Lat", longitude = "Long"}
```
</div>