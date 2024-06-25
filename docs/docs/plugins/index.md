# Plugins

**kmviz** features are extensible through plugins, as independent python packages. They can be used to add support for new provider types or metadata databases, or to add features to the interface by adding new analysis tabs.

## Setup

The plugin package name should matches `kmviz_*` to be automatically detected. Besides, there are no constraints on the package structure. In this example, we follow the classic structure of a poetry-managed project.

``` title="plugin structure"
kmviz_example/
├── kmviz_example
│   ├── assets
│   └── __init__.py
├── poetry.lock
├── pyproject.toml
└── README.md
```

```toml title="pyproject.toml"
[tool.poetry]
name = "kmviz_example"
version = "0.1.0"
description = "A kmviz plugin example"
authors = ["John Doe <john.doe@url.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.9"
numpy = "^1.26.4"
kmviz = "^0.3.1"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

## Plugin interface

The interface to implement is described below. A plugin can implement from one to all of these features.

```py
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
```

## Assets

A plugin can also provide additional assets. Assets will be automatically available if put at the right location. See [instance plugin](plugin_instance.md) example.

## Examples

* [Provider](plugin_provider.md)
* [MetaDB](plugin_metadb.md)
* [Layout](plugin_layout.md)
* [Instance](plugin_instance.md)