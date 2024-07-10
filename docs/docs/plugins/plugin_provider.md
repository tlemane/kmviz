# Provider Plugin

:construction: Work In Progress: The documentation about `Provider` plugins is coming.

## Implementation

Here is an example of plugin providing a new `Provider`.

```python title="Provider Interface"
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

```py title="Provider Plugin"
from kmviz.core.plugin import KmVizPlugin, Provider

class MyProvider(Provider):
    ...

class ProviderPlugin(KmVizPlugin):
    def name(self):
        return "ProviderPlugin"

    def providers(self) -> List[Tuple[str, Provider]]:
        return [("myprovider", MyProvider)]

kmviz_plugin = ProviderPlugin()
```
