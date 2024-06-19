import pytest
import sqlite3
from kmviz.core.metadata.tsv import TsvMetaDB

class TestTsvDB:
    @pytest.fixture(scope="class")
    def db(self):
        return TsvMetaDB(path="tests/kmviz/metadata/test_tsv.tsv", idx="Sample", geodata={"latitude": "Lat", "longitude": "Lon"}, sep=" ")
    
    def test_query(self, db):
        df = db.query(["S1", "S2"])
        assert len(df) == 2
    
    def test_df(self, db):
        df = db.df()
        #c = sqlite3.connect("tests/kmviz/metadata/test_sqlite.sqlite")
        #df.to_sql("table_test", c, index=False)
        assert len(df) == 8

    def test_keys(self, db):
        assert db.keys() == ["ID", "F1", "F2", "Lat", "Lon"]

    def test_geodata(self, db):
        assert db.geodata["latitude"] == "Lat"
        assert db.geodata["longitude"] == "Lon"

    def test_idx(self, db):
        assert db.idx == "Sample"