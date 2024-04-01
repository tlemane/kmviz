import pandas as pd
from typing import List, Set

from .db import MetaDB

class TsvMetaDB(MetaDB):
    def __init__(self, path: str, sample: str, geodata: dict={}, **kwargs) -> None:
        super().__init__(geodata)
        self.data = pd.read_csv(path, **kwargs)
        self.sample = sample

    def connect(self) -> None:
        pass

    def query(self, idx: Set[str]) -> pd.DataFrame:
        return self.data[self.data[self.sample].isin(idx)]

    def df(self) -> pd.DataFrame:
        return self.data

    def keys(self) -> List[str]:
        return list(self.data)
