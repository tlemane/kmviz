# Configuration

**kmviz** can be configured using [`YAML`](https://yaml.org/), [`TOML`](https://toml.io/en/) or [`JSON`](https://www.json.org/json-en.html) configuration files. The documentation uses `TOML` format but complete examples for `YAML` and `JSON` are available at the end of the page. The configuration is divided into different sections which are described below. Note that sections are presented separately for clarity but should be placed in the same file.

## Sections

### `databases`

The `databases` section is required and defines one or more `Database(s)`.

A database is a pair of:

- a `Provider` to perform search is sequence indexes. See [Builtins Provider](../builtins/provider.md)
- a `MetaDB` to associate results with metadata. See [Builtins MetaDB](../builtins/metadb.md)

```toml
# Configure Provider for ExampleDB
[databases.ExampleDB]
type = "kmindex-server"

# Path to a file with some figure presets (json, toml or yaml)
# See Presets section at this end of the page
presets = "./presets.toml"

# The 'params' section corresponds to the parameters passed to the Provider ctor
[databases.ExampleDB.params]
url = "127.0.0.1"
port = 8080

# kmindex-server Provider has two options for users
# Here we set the default values and decide to hide or not
# the option for the users.
[databases.ExampleDB.defaults.z]
value = 2
hide = true
[databases.ExampleDB.defaults.coverage]
value = 0.1
hide = false

# Configure MetaDB for ExampleDB
[databases.ExampleDB.metadata]
type = "tsv"
# The 'params' section corresponds to the parameters passed to the MetaDB ctor
[databases.ExampleDB.metadata.params]
path = "./metadata.tsv"
sep = " "
idx = "Sample"
# If the metadata contains location information
[databases.ExampleDB.metadata.params.geodata]
latitude = "Lat"
longitude = "Long"
```

### `default`

```toml
[default]
database = ["ExampleDB"]      # The database(s) selected by default
configuration = "ExampleDB"   # The database configuration displayed by default

# If true, the database selector is hidden.
# Useful to simplify the usage when the instance
# contains only one database
hide = false
```

### `notif`

The `notif` section allows to set up a mail notifier. See See [Builtins Notifier](../builtins/notifier.md)

### `cache`

**kmviz** requires some caches. For local instances, cache configuration is not a critical point. The example below will work in many cases.

```toml
[cache.result]
type = "disk"
[cache.result.params]
cache_dir = ".kmviz/result"
threshold = 0
default_timeout = 86400

[cache.server]
type = "disk"
[cache.server.params]
cache_dir = ".kmviz/server"
threshold = 0
default_timeout = 86400

[cache.manager]
type = "disk"
[cache.manager.params]
directory = ".kmviz/manager"
```

⚠ For multi-user instances, a particular attention is recommended, see [Deploy](../deploy/index.md).


### `input`

The `input` section is optional and defines the input constraints. The example below corresponds to the default values.

```toml
[input]
max_query_size = 4294967296   # Max number of symbols per query
max_size = 4294967296         # Max number of symbols for all queries
max_query = 4294967296        # Max number of queries
alphabet = "all"              # Use "dna" or "amino" to perform a check when loading the queries
```

### `ui`

The `ui` section is optional and defines the tabs to display.


```toml
[ui]
with_index_tab = false
with_sequence_tab = false
with_map_tab = false
with_plot_tab = false
```

### `auth`

At the moment, **kmviz** has limited authentication support with only [HTTP BasicAuth](https://datatracker.ietf.org/doc/html/rfc7617). Crendentials can be specified directly in the configuration file, or retrieved through the system keyring service. See [jaraco/keyring](https://github.com/jaraco/keyring) for the list of supported keyring backends.


<div class="grid" markdown>

```toml title="config.toml (Inline)"
[auth]
username = "password"
username_2 = "password_2"
```

```toml title="config.toml (Keyring)"
auth = ["username", "username_2"]
```
</div>

### `api`

The `api` section is optinal and allows to configure the [**kmviz** API](../api/index.md).

```toml
[api]
enabled = false
route = "/api"
query_route = "/query"

[api.limits]
max_query_size = 4294967296     # Same as [input] section but only applies on API calls
max_size = 4294967296
max_query = 4294967296
alphabet = "all"
```

Using the previous configuration will produce the following API endpoints:

- `GET  <url>/api`, see [API Infos](../api/info.md)
- `POST <url>/api/query`, see [API Session](../api/session.md)
- `POST <url>/api/query/<database>`, see [API Metadata](../api/metadata.md)

### `html`

The `html` section is optional and allows to change the [Dash HTML template](https://dash.plotly.com/external-resources#customizing-dash's-html-index-template) or add [Meta Tags](https://dash.plotly.com/external-resources#customizing-meta-tags).

```toml
[html]
template = "/path/to/template.html"

[html.metatags]
description = "kmviz ex description"
```

### `plugins`

The `plugins` section allows to load **kmviz** plugins. To read more about plugins, see [Plugins](../plugins/index.md).

```toml
[plugins.kmviz_instance_plugin]
# Parameters passed to the plugins for configuration, can be empty.
key = "value"
```

### Global fields

```toml
# Path to custom stylesheets
# Documentation about kmviz customization using CSS
# will be available later
assets = ["/path/to/custom/style.css"]

# "flex" or "fixed"
# "fixed": A figure is made using the presets but the fields, like "title", are not populated on the interface
# "flex": A preset populates the interface fields and then the figure is updated.
#
# "flex" is probably better but can sometimes slighty slowdown the figure creation.
preset = "fixed"
```

## Configuration CLI

Some configuration helpers are available as small CLI tools: `kmviz config template`, `kmviz config check`, and `kmviz config schema`. See [config CLI](../cli/config.md).
## `YAML` Example

```yaml title="<code>python -m kmviz config template -s all --fmt yaml > config.yaml</code>"
api:
  enabled: false
  limits:
    alphabet: all
    max_query: 4294967296
    max_query_size: 4294967296
    max_size: 4294967296
  query_route: /query
  route: /api
assets: []
auth:
  ex_user: ex_password
cache:
  manager:
    params:
      directory: .kmviz/manager
    type: disk
  result:
    params:
      cache_dir: .kmviz/result
      default_timeout: 86400
      threshold: 0
    type: disk
  server:
    params:
      cache_dir: .kmviz/server
      default_timeout: 86400
      threshold: 0
    type: disk
databases:
  ExampleDB:
    defaults:
      coverage:
        hide: false
        value: 0.1
      z:
        hide: true
        value: 2
    metadata:
      params:
        geodata:
          latitude: Lat
          longitude: Long
        idx: Sample
        path: ./metadata.tsv
        sep: "\t"
      type: tsv
    params:
      port: 8080
      url: 127.0.0.1
    presets: ./presets.toml
    type: kmindex-server
default:
  configuration: ExampleDB
  database:
  - ExDB
  hide: false
html:
  metatags:
    description: kmviz ex description
  template: template.html
input:
  alphabet: all
  max_query: 4294967296
  max_query_size: 4294967296
  max_size: 4294967296
plugins:
  kmviz_example: {}
```
## `JSON` Example

```json title="<code>python -m kmviz config template -s all --fmt json > config.json</code>"
{
    "databases": {
        "ExampleDB": {
            "type": "kmindex-server",
            "params": {
                "url": "127.0.0.1",
                "port": 8080
            },
            "defaults": {
                "z": {
                    "value": 2,
                    "hide": true
                },
                "coverage": {
                    "value": 0.1,
                    "hide": false
                }
            },
            "metadata": {
                "type": "tsv",
                "params": {
                    "path": "./metadata.tsv",
                    "sep": "\t",
                    "idx": "Sample",
                    "geodata": {
                        "latitude": "Lat",
                        "longitude": "Long"
                    }
                }
            },
            "presets": "./presets.toml"
        }
    },
    "input": {
        "max_query_size": 4294967296,
        "max_size": 4294967296,
        "max_query": 4294967296,
        "alphabet": "all"
    },
    "default": {
        "database": [
            "ExDB"
        ],
        "configuration": "ExampleDB",
        "hide": false
    },
    "cache": {
        "result": {
            "type": "disk",
            "params": {
                "cache_dir": ".kmviz/result",
                "threshold": 0,
                "default_timeout": 86400
            }
        },
        "server": {
            "type": "disk",
            "params": {
                "cache_dir": ".kmviz/server",
                "threshold": 0,
                "default_timeout": 86400
            }
        },
        "manager": {
            "type": "disk",
            "params": {
                "directory": ".kmviz/manager"
            }
        }
    },
    "auth": {
        "ex_user": "ex_password"
    },
    "html": {
        "template": "template.html",
        "metatags": {
            "description": "kmviz ex description"
        }
    },
    "api": {
        "enabled": false,
        "route": "/api",
        "query_route": "/query",
        "limits": {
            "max_query_size": 4294967296,
            "max_size": 4294967296,
            "max_query": 4294967296,
            "alphabet": "all"
        }
    },
    "plugins": {
        "kmviz_example": {}
    },
    "assets": [],
    "preset": "flex"
}
```

## Presets

```toml title="presets.toml"
# If true, the presets take precedence over the interface options
priority = true

# Define a map preset 'preset_1'
[map.preset_1]
color = "CovXK"
template = "ggplot2"
[map.preset_1.title]
title_text = "TEST"
title_x = 0.5

# Define a plot preset 'preset_1'
[plot.preset_1]
type = "Scatter"
X = ["CovXK"]
Y = ["CovXB"]

[defaults]
map = "preset_1"
plot = "preset_1"
```

<details>
<summary>Available options</summary>

```py
class title_presets(BaseModel):
    title_text: Optional[str]=None
    title_font_size: Optional[int]=None
    title_font_familiy: Optional[Literal["Arial", "Balto", "Courier New", "Droid Sans", "Droid Serif", "Droid Sans Mono", "Gravitas One", "Old Standard TT", "Open Sans", "Overpass", "PT Sans Narrow", "Raleway", "Times New Roman"]]=None
    title_font_color: Optional[str]=None

    title_xanchor: Optional[Literal["auto", "left", "center", "right"]]=None
    title_xref: Optional[Literal["container", "paper"]]=None
    title_x: Annotated[Optional[float], Ge(0.0), Le(1.0)]=None

    title_yanchor: Optional[Literal["auto", "top", "middle", "bottom"]]=None
    title_yref: Optional[Literal["container", "paper"]]=None
    title_y: Annotated[Optional[float], Ge(0.0), Le(1.0)]=None

class legend_presets(BaseModel):
    legend_title_text: Optional[str]=None
    legend_title_font_size: Optional[int]=None
    legend_title_font_familiy: Optional[Literal["Arial", "Balto", "Courier New", "Droid Sans", "Droid Serif", "Droid Sans Mono", "Gravitas One", "Old Standard TT", "Open Sans", "Overpass", "PT Sans Narrow", "Raleway", "Times New Roman"]]=None
    legend_title_font_color: Optional[str]=None

    legend_xanchor: Optional[Literal["auto", "left", "center", "right"]]=None
    legend_xref: Optional[Literal["container", "paper"]]=None
    legend_x: Annotated[Optional[float], Ge(0.0), Le(1.0)]=None
    legend_yanchor: Optional[Literal["auto", "top", "middle", "bottom"]]=None
    legend_yref: Optional[Literal["container", "paper"]]=None
    legend_y: Annotated[Optional[float], Ge(0.0), Le(1.0)]=None

    legend_indentation: Annotated[Optional[int], Ge(-15), Le(100)]=None
    legend_orientation: Optional[Literal["v", "h"]]=None

    legend_font_size: Optional[int]=None
    legend_font_familiy: Optional[Literal["Arial", "Balto", "Courier New", "Droid Sans", "Droid Serif", "Droid Sans Mono", "Gravitas One", "Old Standard TT", "Open Sans", "Overpass", "PT Sans Narrow", "Raleway", "Times New Roman"]]=None
    legend_font_color: Optional[str]=None

    legend_borderwidth: Annotated[Optional[int], Ge(0), Le(100)]=None
    legend_bordercolor: Optional[str]=None
    legend_bgcolor: Optional[str]=None

class map_presets(BaseModel):
    color: Optional[str]=None
    size: Optional[str]=None
    text: Optional[str]=None
    symbol: Optional[str]=None
    animation_frame: Optional[str]=None
    animation_group: Optional[str]=None
    template: Optional[str]=None
    projection: Optional[str]=None
    color_seq_continuous_scale: Optional[str]=None
    color_div_continuous_scale: Optional[str]=None
    color_cyc_continuous_scale: Optional[str]=None
    color_continuous_midpoint: Optional[Union[int, float]]=None
    opacity: Annotated[Optional[float], Ge(0.0), Le(1.0)]=None
    size_max: Annotated[Optional[int], Ge(0), Le(50)]=None
    color_discrete_map: Optional[Dict[Any, str]]=None
    symbol_map: Optional[Dict[Any, str]]=None
    color_discrete_sequence: Optional[List[str]]=None
    symbol_sequence: Optional[List[str]]=None

    title: Optional[title_presets]=title_presets()
    legend: Optional[legend_presets]=legend_presets()

class plot_presets(BaseModel):
    type: str

    X: Optional[List[str]]=None
    Y: Optional[List[str]]=None
    Z: Optional[List[str]]=None
    color: Optional[str]=None
    size: Optional[str]=None
    text: Optional[str]=None
    symbol: Optional[str]=None
    pattern_shape: Optional[str]=None
    base: Optional[str]=None
    line_dash: Optional[str]=None
    line_group: Optional[str]=None
    dimensions: Optional[List[str]]=None
    values: Optional[str]=None
    names: Optional[str]=None

    animation_frame: Optional[str]=None
    animation_group: Optional[str]=None
    template: Optional[str]=None

    color_seq_continuous_scale: Optional[str]=None
    color_div_continuous_scale: Optional[str]=None
    color_cyc_continuous_scale: Optional[str]=None
    color_continuous_midpoint: Optional[Union[int, float]]=None
    opacity: Annotated[Optional[float], Ge(0.0), Le(1.0)]=None
    size_max: Annotated[Optional[int], Ge(0), Le(50)]=None

    color_discrete_map: Optional[Dict[Any, str]]=None
    symbol_map: Optional[Dict[Any, str]]=None
    color_discrete_sequence: Optional[List[str]]=None
    symbol_sequence: Optional[List[str]]=None

    pattern_shape_map: Optional[Dict[Any, str]]=None
    line_dash_map: Optional[Dict[Any, str]]=None
    pattern_shape_sequence: Optional[List[str]]=None
    line_dash_sequence: Optional[List[str]]=None

    trendline: Optional[Literal["ols", "lowess", "rolling", "expanding", "ewm"]]=None
    trendline_scope: Optional[Literal["trace", "overall"]]=None
    trendline_options: Optional[Dict[Any, str]]=None

    marginal_x: Optional[Literal["rug", "box", "violin", "histogram"]]=None
    marginal_y: Optional[Literal["rug", "box", "violin", "histogram"]]=None

    facet_row: Optional[str]=None
    facet_col: Optional[str]=None
    facet_col_spacing: Annotated[Optional[float], Ge(0.0), Le(1.0)]=None
    facet_row_spacing: Annotated[Optional[float], Ge(0.0), Le(1.0)]=None
    facet_col_wrap: Annotated[Optional[int], Ge(0), Le(10)]=None

    title: Optional[title_presets]=title_presets()
    legend: Optional[legend_presets]=legend_presets()
```
</details>