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

    def connect(self) -> None:
        self.db = sqlite3.connect(self.path)

    def query(self, keys: Set[str]) -> pd.DataFrame:
        keys_str = (f"'{x}'" for x in keys)
        return pd.read_sql(f"SELECT * FROM {self.table} WHERE {self.idx} IN ({','.join(keys_str)})", self.db)

    def df(self) -> pd.DataFrame:
        return pd.read_sql(f"SELECT * from '{self.table}'", self.db)

    def keys(self) -> List[str]:
        cur = self.db.execute(f"SELECT * from '{self.table}'")
        return list(map(lambda x: x[0], cur.description))

