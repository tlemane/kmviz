from kmviz.core.provider import Provider
from kmviz.core.metadata.db import MetaDB
from kmviz.core import KmVizError
from typing import List, Tuple, Any, Union
import importlib
import pkgutil

plugin_prefix = "kmviz_"

class KmVizPlugin:

    def providers(self) -> List[Provider]:
        return []

    def databases(self) -> List[MetaDB]:
        return []

    def layouts(self) -> List[Tuple[str, Any]]:
        return []

    def external_scripts(self) -> List[Union[dict, str]]:
        return []

    def external_styles(self) -> List[Union[dict, str]]:
        return []

    def help(self) -> Any:
        return None

    def is_instance_plugin(self) -> bool:
        return False

    def instance(self) -> Any:
        return None

    def name(self) -> str:
        return None

def installed_plugins() -> List[str]:
    res = []
    for finder, name, ispkg in pkgutil.iter_modules():
        if name.startswith("kmviz_"):
            res.append(name)
    return res

def search_for_plugins(modules: List[str]):
    plugins = {}

    for name in modules:
        if name.startswith("kmviz_"):
            try:
                module = importlib.import_module(name)
                plugins[name] = module.kmviz_plugin

                if not isinstance(plugins[name], KmVizPlugin):
                    raise KmVizError(f"Found module {name}, but 'kmviz_plugin' is not an instance of KmVizPlugin")
            except ImportError as e:
                raise KmVizError(f"Module '{name}' not found, installed plugins are [{','.join(installed_plugins())}]")

    return plugins


