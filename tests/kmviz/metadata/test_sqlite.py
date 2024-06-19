import pytest
from kmviz.core.metadata.sqlite import SQLiteMetaDB

class TestSQLiteDB:
    @pytest.fixture(scope="class")
    def db(self):
        return SQLiteMetaDB(path="tests/kmviz/metadata/test_sqlite.sqlite", table="table_test", idx="ID", geodata={"latitude": "Lat", "longitude": "Lon"})
    
    @pytest.fixture(scope="class")
    def connect(self, db):
        db.connect()
        return db

    def test_connect(self, db):
        db.connect()

    def test_query(self, connect):
        df = connect.query(["S1", "S2"])
        assert len(df) == 2
    
    def test_df(self, connect):
        df = connect.df()
        assert len(df) == 8

    def test_keys(self, connect):
        assert connect.keys() == ["ID", "F1", "F2", "Lat", "Lon"]

    def test_geodata(self, connect):
        assert connect.geodata["latitude"] == "Lat"
        assert connect.geodata["longitude"] == "Lon"

    def test_idx(self, connect):
        assert connect.idx == "ID"