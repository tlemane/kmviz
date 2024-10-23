import pandas as pd
from typing import List, Set
from .db import MetaDB
import mysql.connector
from sqlalchemy import create_engine

def _make_sqlalchemy_connection(user: str, password: str, host: str, dbname: str, port: int):
    template = "mysql+mysqlconnector://{user}:{password}@{server}:{port}/{dbname}"
    template_noport = "mysql+mysqlconnector://{user}:{password}@{server}/{dbname}"
    if port:
        return create_engine(template.format(
            user=user, password=password, server=host, port=port, dbname=dbname))
    else:
        return create_engine(template_noport.format(
            user=user, password=password, server=host, dbname=dbname))

class MySQLMetaDB(MetaDB):
    def __init__(self, idx: str, geodata: str, host: str, user: str, password: str, database: str, table: str, port: int=None) -> None:
        super().__init__(idx, geodata)
        self.host = host
        self.table = table
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.db = None
        self.cursor = None

    def _rename_idx(self, df: pd.DataFrame) -> pd.DataFrame:
        df.rename(columns={self.idx: "ID"}, inplace=True)
        return df

    def connect(self) -> None:
        self.db = _make_sqlalchemy_connection(self.user, self.password, self.host, self.database, self.port)

    def query(self, keys: Set[str]) -> pd.DataFrame:
        keys_str = (f"'{x}'" for x in keys)
        df = pd.read_sql(f"SELECT * FROM {self.table} WHERE {self.idx} IN ({','.join(keys_str)})", self.db)
        return self._rename_idx(df)

    def df(self) -> pd.DataFrame:
        df = pd.read_sql(f"SELECT * from {self.table}", self.db)
        return self._rename_idx(df)

    def keys(self) -> List[str]:
        return list(self._rename_idx(pd.read_sql(f"SELECT * from {self.table} WHERE 1=0", self.db)))