from kmviz.core.provider import Provider
from kmviz.core.metadata.db import MetaDB
from kmviz.core import KmVizError
from typing import List, Tuple, Any, Union
import importlib
import pkgutil

plugin_prefix = "kmviz_"

class KmVizPlugin:

    def providers(self) -> List[Tuple[str, Provider]]:
        """
        :returns: The providers implemented by the plugin, as list of tuples <name,'Provider'>
        """
        return []

    def databases(self) -> List[Tuple[str, MetaDB]]:
        """
        :returns: The metadbs implemented by the plugin, as list of tuples <name,'MetaDB'>
        """
        return []

    def layouts(self) -> List[Tuple[str, Any, str]]:
        """
        :returns: The layouts implemented by the plugin, as list of tuples <name, dash_component, icon_name>
        """
        return []

    def external_scripts(self) -> List[Union[dict, str]]:
        """
        :returns: A list of js scripts to load, see https://dash.plotly.com/external-resources
        """
        return []

    def external_styles(self) -> List[Union[dict, str]]:
        """
        :returns: A list of css stylesheets to load, see https://dash.plotly.com/external-resources
        """
        return []

    def help(self) -> Any:
        """
        :returns: A Dash Component which will be displayed in the help tab.
        """
        return None

    def is_instance_plugin(self) -> bool:
        """
        :returns: True if the plugin is an instance plugin, False otherwise
        """
        return False

    def instance(self) -> Any:
        """
        :returns: A Dash Component which will be used as a homepage
        """
        return None

    def name(self) -> str:
        """
        :returns: The plugin name
        """
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


