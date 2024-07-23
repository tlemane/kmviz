from dash import Patch, ALL, MATCH
from dataclasses import dataclass
from typing import Any, List, Dict
from typing_extensions import Self

class IDFactory:
    def __init__(self, name: str) -> None:
        self._name = name
        self._children: List[Self] = []
        self._string_register: Dict[str, Any] = {}
        self._index_register: Dict[str, Any] = {}
        self._register: List[str] = []
        self._index: int=0

    def _make_index_id(self, index: Any) -> Dict[str, Any]:
        if index is None:
            iid = { "type": self._name, "index": self._index }
            self._index += 1
        else:
            idd = { "type": self._name, "index": index}

        r = f"{idd['type']}@{idd['index']}"
        if r not in self._index_register:
            self._index_register[r] = idd
            self._register.append(r)

        return idd

    def _make_string_id(self, index: str) -> str:
        r = f"{self._name}-{index}"
        if r not in self._string_register:
            self._string_register[r] = None
            self._register.append(r)
        return r

    def new(self, suffix: str) -> Self:
        self._children.append(IDFactory(f"{self.name}-{suffix}"))
        return self._children[-1]

    def __getitem__(self, index: str) -> str:
        return self._make_string_id(index)

    def __call__(self, index: str, as_string: bool=False) -> Dict[str, Any]:
        r = self._make_index_id(index)
        if as_string:
            return f"{r['type']}-{r['index']}"
        else:
            return r

    def get_all(self, child: bool=True, s: bool=True, i: bool=True):
        ret = []

        if s:
            for k in self._string_register:
                ret.append(k)
        if i:
            for v in self._index_register.values():
                ret.append(v)

        if child:
            for c in self._children:
                ret.extend(c.get_all(child, s, i))

        return ret

    @property
    def all(self):
        return {"type": self._name, "index": ALL}

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return self._name

@dataclass
class FactoryStore:
    kmviz: IDFactory = IDFactory("kmviz")
    store: IDFactory = None
    side: IDFactory = None
    tabs: IDFactory = None

    index: IDFactory = None
    table: IDFactory = None
    map: IDFactory = None
    plot: IDFactory = None
    session: IDFactory = None

    input: IDFactory = None
    submit: IDFactory = None
    config: IDFactory = None
    pom: IDFactory = None
    sequence: IDFactory = None
    help: IDFactory = None

    def __post_init__(self):
        self.store = self.kmviz.new("store")
        self.side = self.kmviz.new("side")
        self.tabs = self.kmviz.new("tabs")
        self.plugin = self.kmviz.new("plugin")
        self.index = self.tabs.new("index")
        self.table = self.tabs.new("table")
        self.map = self.tabs.new("map")
        self.plot = self.tabs.new("plot")
        self.sequence = self.tabs.new("sequence")
        self.submit = self.kmviz.new("submit")
        self.input = self.kmviz.new("input")
        self.config = self.kmviz.new("config")
        self.pom = self.side.new("pom")
        self.session = self.kmviz.new("session")
        self.help = self.tabs.new("help")

    def register(self, f: IDFactory, name: str):
        if not hasattr(self, name):
            setattr(self, name, f)

kid = FactoryStore()

def _split_idx(idx):
    if isinstance(idx, dict):
        return idx["type"], idx["index"]
    else:
        return idx.rsplit("-", 1)

def _formatted_idx(idx):
    t, i = _split_idx(idx)

    if isinstance(idx, dict):
        return f'("{i}")'
    else:
        return f'["{i}"]'
