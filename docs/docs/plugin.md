**kmviz** features are extensible through plugins, as independent python packages. They can be used to add support for new provider types or metadata databases, or to add features to the interface by adding new analysis tabs. 

If you want to deploy an instance for a specific project, you can use [instance plugins](.#instance-plugin). These plugins are useful for defining specific elements for a project, such as a home page or specific help, details about indexes and associated metadata.

This section describes a step-by-step plugin implementation, see [`kmviz_example` plugin](https://github.com/tlemane/kmviz/plugins/kmviz_example) for the complete source code.

## Setup

The plugin package name should matches `kmviz_*` to be automatically detected. Besides, there are no constraints on the package structure. In this example, we follow the classic structure of a poetry-managed project.

``` title="plugin structure"
kmviz_example/
├── kmviz_example
│   ├── assets
│   └── __init__.py
├── poetry.lock
├── pyproject.toml
└── README.md
```

```toml title="pyproject.toml"
[tool.poetry]
name = "kmviz_example"
version = "0.1.0"
description = "A kmviz plugin example"
authors = ["John Doe <john.doe@url.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.9"
numpy = "^1.26.4"
kmviz = "^0.1.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

## Implementation

### Provider

```py title="Provider Interface"
class Provider(ABC):
    def __init__(self, name: str):
        self._name = name
        self.index_infos: Dict[str, Any] = None
        self.db: MetaDB = None
        self.options = {}
        self._presets = {}

    @abstractmethod
    def connect(self):
        """
        Initialization, like database login, should take place here
        """
        ...

    @abstractmethod
    def index_list(self) -> List[str]:
        """
        :returns: The list of sub-index names
        """
        ...

    @abstractmethod
    def query(self, query: Query, options: dict, idx: str) -> QueryResponse:
        """
        :param query: The query
        :param options: The user-defined options 
        :param idx: A unique id representing the query
        :returns: T
        """
        ...

    @abstractmethod
    def samples(self, index=None) -> Union[Dict[str, list], List[str]]:
        """
        :param index: The sub-index name
        :returns: The list of sample indexed by the sub-index, or a dict of list with one key per sub-index
        """
        ...

    @abstractmethod
    def kmer_size(self) -> int:
        """
        :returns: The kmer size for kmer-based index, 0 otherwise
        """
        ...
```


```py
self.options = {
    "coverage": RangeOption("coverage", 0.2, min=0.0, max=1.0, step=0.05)
}
```

![image](assets/option.png)


```py title="Builtin options"
@dataclass
class NumericOption(ProviderOption):
    min: Optional[Union[int, float]]
    max: Optional[Union[int, float]]
    value: Union[int, float] = None

@dataclass
class ChoiceOption(ProviderOption):
    choices: Iterable[Union[str, int, float]]
    value: Union[str, int, float] = None

@dataclass
class MultiChoiceOption(ProviderOption):
    choices: Iterable[Union[str, int, float]]
    value: Iterable[Union[str, int, float]] = None

@dataclass
class RangeOption(ProviderOption):
    min: Union[int, float]
    max: Union[int, float]
    step: Union[int, float]
    value: [int, float] = None

@dataclass
class TextOption(ProviderOption):
    value: str = None
```

### MetaDB

```py title="MetaDB Interface"
class MetaDB(ABC):
    def __init__(self, idx: str, geodata: Dict[str, str] = {}) -> None:
        self._geodata = geodata
        self._idx = idx

    @abstractmethod
    def connect(self):
        """
        Initialization, like database login, should take place here
        """
        ...

    @abstractmethod
    def query(self, keys: List[str]) -> pd.DataFrame:
        """
        Select a subset of metadata

        :param keys: A sequence of identifiers
        :returns: A dataframe with the metadata corresponding to the keys
        """
        ...

    @abstractmethod
    def df(self) -> pd.DataFrame:
        """
        Get all metadata

        :returns: A dataframe with all metadata
        """
        ...

    @abstractmethod
    def keys(self) -> List[str]:
        """
        Get all fields

        :returns: The list of all fields
        """
        ...
```



## Plugin interface

```py title="The KmVizPlugin interface"
class KmVizPlugin:

    def providers(self) -> List[Provider]:
        return []

    def databases(self) -> List[MetaDB]:
        return []

    def layouts(self) -> List[Tuple[str, Any]]:
        return []

    def external_scripts(self) -> List[Union[dict, str]]:
        return []

    def external_styles(self) -> List[Union[dict, str]]:
        return []

    def help(self) -> Any:
        return None

    def is_instance_plugin(self) -> bool:
        return False

    def instance(self) -> Any:
        return None

    def name(self) -> str:
        return None
```


### Assets

### Layout

## Instance plugin