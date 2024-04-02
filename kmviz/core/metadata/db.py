from abc import ABC, abstractmethod
from typing import List, Dict
import pandas as pd

class MetaDB(ABC):
    def __init__(self, idx: str, geodata: Dict[str, str] = {}) -> None:
        self._geodata = geodata
        self._idx = idx

    @abstractmethod
    def connect(self):
        ...

    @abstractmethod
    def query(self, keys: List[str]) -> pd.DataFrame:
        ...

    @abstractmethod
    def df(self) -> pd.DataFrame:
        ...

    @abstractmethod
    def keys(self) -> List[str]:
        ...

    @property
    def geodata(self) -> dict:
        return self._geodata

    @property
    def idx(self) -> str:
        return self._idx




