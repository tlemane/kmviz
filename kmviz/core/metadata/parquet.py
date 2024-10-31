from .db import MetaDB
import duckdb
from typing import List

class ParquetDB(MetaDB):
    def __init__(self, idx: str, geodata, files: List[str]):
        super().__init__(idx, geodata)
        self._files = files

    def connect(self) -> None:
        return None

    def query(self, keys):
        keys_str = (f"'{x}'" for x in keys)
        db = duckdb.read_parquet(self._files)
        Id = self.idx
        Q = f"""
            SELECT *
            FROM db
            WHERE {Id} IN ({','.join(keys_str)})
        """
        d = duckdb.sql(Q).df()
        d.rename(columns={self.idx: "ID"}, inplace=True)
        return d

    def df(self):
        return None

    def keys(self):
        return None