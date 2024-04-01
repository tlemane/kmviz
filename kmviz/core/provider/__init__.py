from .provider import Providers, Provider
from .kmindex import KmindexServerProvider

from kmviz.core.metadata import make_metadb_from_dict

PROVIDERS = {
    "kmindex-server": KmindexServerProvider
}

def make_provider_from_dict(name, d):
    if d["type"] not in PROVIDERS:
        raise RuntimeError("")

    p = PROVIDERS[d["type"]](name=name, **d["params"])
    metadb = make_metadb_from_dict(d["metadata"])
    p.attach_metadata(metadb)

    presets = { "map": {}, "plot": {}}

    if "presets" in d:
        pconf = d["presets"]
        for key in ["map", "plot"]:
            if key in pconf:
                for e in pconf[key]:
                    if not "priority" in e:
                        e["priority"] = False
                    presets[key][e["name"]] = e

        p.set_presets(presets)
    return p
