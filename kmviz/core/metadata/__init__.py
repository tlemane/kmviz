from .tsv import TsvMetaDB
from .sqlite import SQLiteMetaDB
from .mysql import MySQLMetaDB
from .db import MetaDB
from kmviz.core import KmVizError

METADBS = {
    "tsv": TsvMetaDB,
    "sqlite": SQLiteMetaDB,
    "mysql": MySQLMetaDB,
}




