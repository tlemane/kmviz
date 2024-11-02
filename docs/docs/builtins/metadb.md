# MetaDB

## `SQLite`

|Parameter|Description|Default|Required|
|---|---|---|---|
|path|Path to the `sqlite` file |-|:white_check_mark:|
|table|Table name|-|:white_check_mark:|
|idx|Column containing identifiers|-|:white_check_mark:|
|geodata|Columns containing geographical data, if applicable|-|:x:|

<div class="grid" markdown>

```yaml title="sqlite_ex.yaml"
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

```toml title="sqlite_ex.toml"
[databases.Example.metadata]
type = "sqlite"
[databases.Example.metadata.params]
path = "./metadata.sqlite"
table = "table"
idx = "Sample"
geodata = { latitude = "Lat", longitude = "Long"}
```
</div>


## `TSV File`

|Parameter|Description|Default|Required|
|---|---|---|---|
|path|Path to the `tsv` file |-|:white_check_mark:|
|sep|Separator|'\t'|:x:|
|idx|Column containing identifiers|-|:white_check_mark:|
|geodata|Columns containing geographical data, if applicable|-|:x:|

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

## `MySQL / MariaDB`

|Parameter|Description|Default|Required|
|---|---|---|---|
|host|DB server url|-|:white_check_mark:|
|user|Username|-|:white_check_mark:|
|password|Password|-|:white_check_mark:|
|database|Database name|-|:white_check_mark:|
|table|Table name|-|:white_check_mark:|
|port|DB server port|3306|:x:|
|idx|Column containing identifiers|-|:white_check_mark:|
|geodata|Columns containing geographical data, if applicable|-|:x:|

<div class="grid" markdown>

```yaml title="mysql_ex.yaml"
metadata:
  type: "mysql"
  params:
    host: "localhost"
    user: "root"
    password: "password"
    database: "kmvizdb"
    table: "table"
    geodata:
      latitude: "Lat"
      longitude: "Long"
```

```toml title="mysql_ex.toml"
[databases.Example.metadata]
type = "mysql"
[databases.Example.metadata.params]
host ="localhost"
user = "root"
password = "password"
database = "kmvizdb"
table = "table"
idx = "Sample"
geodata = { latitude = "Lat", longitude = "Long"}
```
</div>

## `Parquet`

|Parameter|Description|Default|Required|
|---|---|---|---|
|files|List of parquet files|-|:white_check_mark:|
|idx|Column containing identifiers|-|:white_check_mark:|
|geodata|Columns containing geographical data, if applicable|-|:x:|

<div class="grid" markdown>

```yaml title="parquet_ex.yaml"
metadata:
  type: "parquet"
  params:
    files: ["/path/to/file.parquet"]
    idx: "Sample"
    geodata:
      latitude: "Lat"
      longitude: "Long"
```

```toml title="parquet_ex.toml"
[databases.Example.metadata]
type = "parquet"
[databases.Example.metadata.params]
files = ["/path/to/file.parquet"]
idx = "Sample"
geodata = { latitude = "Lat", longitude = "Long"}
```
</div>

