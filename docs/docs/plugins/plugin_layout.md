# Layout

If a plugin provides one or more layouts, they will appear as new tabs in the interface. Note that this section is a work in progress. The identifiers and descriptions of the dash components that can be used to interact with **kmviz** will be described in the near future.

## Implementation

Here is an example of a plugin providing a new layout. See [:fontawesome-brands-github: kmviz_instance_plugin](https://github.com/tlemane/kmviz/plugins/kmviz_instance_plugin) for a complete example.

```py title="kmviz_layout_plugin/__init__.py"
from kmviz.core.plugin import KmVizPlugin
from typing import List, Tuple, Any

def make_layout():
    res = html.Div([
        "New Layout example"
    ])
    return res

class KmVizLayoutPlugin(KmVizPlugin):
    def name(self):
        return "KmVizLayoutPlugin"

    def layouts(self) -> List[Tuple[str, Any, str]]:
        return [("NewTab", make_layout(), "mdi:new-box")]

kmviz_plugin = KmVizLayoutPlugin()
```
