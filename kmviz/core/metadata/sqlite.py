import pandas as pd
from typing import List, Set
from .db import MetaDB
import sqlite3

class SQLiteMetaDB(MetaDB):
    def __init__(self, path: str, idx: str, table: str, geodata: dict={}, **kwargs) -> None:
        super().__init__(idx, geodata)
        self.db = None
        self.path = path
        self.table = table

    def _rename_idx(self, df: pd.DataFrame) -> pd.DataFrame:
        df.rename(columns={self.idx: "ID"}, inplace=True)
        return df

    def connect(self) -> None:
        self.db = sqlite3.connect(self.path)

    def query(self, keys: Set[str]) -> pd.DataFrame:
        keys_str = (f"'{x}'" for x in keys)
        df = pd.read_sql(f"SELECT * FROM {self.table} WHERE {self.idx} IN ({','.join(keys_str)})", self.db)
        return self._rename_idx(df)

    def df(self) -> pd.DataFrame:
        df = pd.read_sql(f"SELECT * from '{self.table}'", self.db)
        return self._rename_idx(df)

    def keys(self) -> List[str]:
        cur = self.db.execute(f"SELECT * from '{self.table}'")
        return list(map(lambda x: x[0], cur.description))

