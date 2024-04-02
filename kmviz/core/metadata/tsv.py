import pandas as pd
from typing import List, Set

from .db import MetaDB

class TsvMetaDB(MetaDB):
    def __init__(self, path: str, idx: str, geodata: dict={}, **kwargs) -> None:
        super().__init__(idx, geodata)
        self.data = pd.read_csv(path, **kwargs)
        self.data.rename(columns={self.idx: "ID"}, inplace=True)

    def connect(self) -> None:
        pass

    def query(self, keys: Set[str]) -> pd.DataFrame:
        return self.data[self.data["ID"].isin(keys)]

    def df(self) -> pd.DataFrame:
        return self.data

    def keys(self) -> List[str]:
        return list(self.data)
