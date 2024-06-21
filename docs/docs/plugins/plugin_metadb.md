# MetaDB Plugin

## Implementation

Here is an example of plugin providing a new `MetaDB`.

```python title="MetaDB Interface"
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

To learn how to implement a new `MetaDB`, look at the builtin implementations: [:fontawesome-brands-github: metadata](https://github.com/tlemane/kmviz/kmviz/core/metadata).

```py title="MetaDB Plugin"
from kmviz.core.plugin import KmVizPlugin, MetaDB

class MyMetaDB(MetaDB):
    ...

class MetaDBPlugin(KmVizPlugin):
    def name(self):
        return "MetaDBPlugin"

    def databases(self) -> List[Tuple[str, MetaDB]]:
        return [("mymetadb", MyMetaDB)]

kmviz_plugin = MetaDBPlugin()
```


