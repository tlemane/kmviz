from abc import ABC, abstractmethod
from typing import Union, Dict, Any, List

import pandas as pd

from dataclasses import dataclass
from kmviz.core.query import QueryResponse, Query
from kmviz.core.metadata.db import MetaDB

from .options import ProviderOption

class Provider(ABC):
    def __init__(self, name: str):
        self._name = name
        self.index_infos: Dict[str, Any] = None
        self.db: MetaDB = None
        self.active = set()
        self.options = {}
        self._presets = {}

    @abstractmethod
    def connect(self):
        ...

    @abstractmethod
    def index_list(self) -> List[str]:
        ...

    @abstractmethod
    def query(self, query: Query, options: dict, idx: str) -> QueryResponse:
        ...

    @abstractmethod
    def samples(self, index=None) -> Union[Dict[str, list], List[str]]:
        ...

    @abstractmethod
    def kmer_size(self) -> int:
        ...

    @property
    def presets(self) -> dict:
        return self._presets

    @property
    def ready(self) -> bool:
        return True

    def options(self) -> Dict[str, ProviderOption]:
        return self.options

    def set_presets(self, presets: dict):
        self._presets = presets

    def set_active(self, indexes: List[str]):
        self.active = set(indexes)

    def name(self) -> str:
        return self._name

    def nb_samples(self, index=None) -> int:
        return len(self.samples(index))

    def infos(self) -> Dict[str, Any]:
        return self.index_infos

    def infos_df(self) -> pd.DataFrame:
        return pd.DataFrame.from_dict(self.index_infos)

    def attach_metadata(self, metadata: MetaDB) -> None:
        self.db = metadata

    def filter_metadata(self, query_metadata: pd.DataFrame) -> pd.DataFrame:
        return pd.merge(self.db.df(), query_metadata, on=[])

@dataclass
class _Opt:
    value: Any

class Providers:
    def __init__(self):
        self._providers = {}
        self._active = set()

    def add(self, provider: Provider, active=False) -> None:
        self._providers[provider.name()] = provider
        if active:
            self._active.add(provider.name())

    def set_active(self, providers: List[str]):
        self._active = set(providers)

    def list(self) -> List[str]:
        return list(self._providers.keys())

    def all(self):
        return self._providers

    def active(self) -> set:
        return self._active

    def get(self, name: str):
        return self._providers[name]

    def query(self, query: Query, actives: list, options: dict, idx: str) -> Dict[str, QueryResponse]:
        res = {}
        for p in actives:
            opt = { k: _Opt(v) for k, v in options[p].items()}
            res[self._providers[p].name()] = self._providers[p].query(query, opt, idx)
        return res


