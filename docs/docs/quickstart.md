The repository includes small data and configuration files to quickly run an instance of **kmviz** using a local index constructed with [kmindex](https://tlemane.github.io/kmindex/). The example mimics the Tara Ocean data: each input sample corresponds to a sampling station in the oceans and is associated with metadata.

### Requirements

* [kmindex](https://tlemane.github.io/kmindex/), see [instructions](https://tlemane.github.io/kmindex/installation/) for installation. We recommend the conda installation that includes **kmindex** dependencies.
* **kmviz** should be installed, see [Installation](installation.md).

### Construct an index 

```bash
cd tests/small_example
kmindex build -i index -f fof.txt -r my_index -d my_index_store -k 25 --hard-min 1 --bloom-size 100000 --cpr --nb-partitions 8 --threads 8
```

### Start a **kmindex-server**

Start a query server at `127.0.0.1:8080`. See `kmindex-server --help` if you need custom configuration.
```bash
cd tests/small_example
kmindex-server -i index
```

### Start **kmviz**

```bash
poetry shell
cd tests/small_example
python -m kmviz.app --config config.toml
```

```toml title="config.toml"
[databases]

[databases.SMALL]
type = "kmindex-server"
[databases.SMALL.params]
url = "127.0.0.1"
port = 8080
[databases.SMALL.metadata]
type = "tsv"
[databases.SMALL.metadata.params]
path = "./metadata.tsv"
sep = "\t"
idx = "Sample"
geodata = { latitude = "Lat", longitude = "Long"}

[manager]
type = "disk"
params.directory = "./kmviz_manager_cache"

[cache]
params.directory = "./kmviz_result_cache"
params.size_limit = 20000000

[auth]
small = "small-password"
```

The **kmviz** instance is now available at `127.0.0.1:8050`.