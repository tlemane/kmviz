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

    def add(self, provider: Provider) -> None:
        self._providers[provider.name()] = provider

    def list(self) -> List[str]:
        return list(self._providers.keys())

    def all(self):
        return self._providers

    def get(self, name: str):
        return self._providers[name]

    def query(self, query: Query, actives: list, options: dict, idx: str) -> Dict[str, QueryResponse]:
        res = {}
        for p in actives:
            opt = { k: _Opt(v) for k, v in options[p].items()}
            res[self._providers[p].name()] = self._providers[p].query(query, opt, idx)
        return res


