from abc import ABC, abstractmethod
from typing import List
import pandas as pd

class MetaDB(ABC):
    def __init__(self, geodata = {}, **kwargs):
        self._geodata = geodata

    @abstractmethod
    def connect(self):
        ...

    @abstractmethod
    def query(self, idx: List[str]) -> pd.DataFrame:
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




