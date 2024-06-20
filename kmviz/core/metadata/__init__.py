from .tsv import TsvMetaDB
from .sqlite import SQLiteMetaDB
from .mysql import MySQLMetaDB
from importlib import import_module
from kmviz.core import KmVizError

METADBS = {
    "tsv": TsvMetaDB,
    "sqlite": SQLiteMetaDB,
    "mysql": MySQLMetaDB,
}

def make_metadb_from_dict(d):
    if d["type"] not in METADBS:
        raise KmVizError(f"MetaDB type not recognized ('{d['type']}'), [{','.join(METADBS.keys())}]")

    return  METADBS[d["type"]](**d["params"])



