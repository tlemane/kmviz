from .tsv import TsvMetaDB
from importlib import import_module

METADBS = {
    "tsv": TsvMetaDB
}

def make_metadb_from_dict(d):
    if d["type"] not in METADBS:
        raise RuntimeError("")

    return  METADBS[d["type"]](**d["params"])



