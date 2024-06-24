# Instance plugin

## Implementation

Here is an example of `instance plugin` implementation. A complete example is available at [:fontawesome-brands-github: kmviz_instance_plugin](https://github.com/tlemane/kmviz/plugins/kmviz_instance_plugin).

```py
from typing import Any
from kmviz.core.plugin import KmVizPlugin

from dash import dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash_extensions.enrich import html

from typing import List, Tuple, Any

class InstancePlugin(KmVizPlugin):
    def is_instance_plugin(self) -> bool:
        return True

    def name(self) -> str:
        return "InstancePlugin"

    def instance(self) -> html.Div:
        layout = html.Div([
            dcc.Markdown("""
            ## Welcome to the kmviz demo instance!
            Here is an example of what happens when **kmviz** loads an *instance* plugin.
            In addition to the usual plugin features, an instance plugin can provide
            a homepage to describe the instance content and provide some help.
            Here we loaded 'kmviz_instance_plugin'.
            When a homepage is provided, the **kmviz** dashboard is available
            at `{url}/dashboard` and the plugin should provide a link to it on the
            homepage, as the button below.
            """),
            html.A(
                dmc.Button(
                    "Go to dashboard",
                    leftIcon=DashIconify(icon="noto:rocket", width=20),
                    style={"position":"fixed", "top": "50%", "left":"50%"}
                ),
                href="/dashboard"
            ),
            dcc.Markdown("""
            *Instance* plugin can also provide additional assets:
            """),
            html.Img(src="assets/_kmviz_instance_plugin_assets/placeholder.png")
        ])

        return layout

kmviz_plugin = InstancePlugin()
```

Assets will be automatically available if put at the right location, *i.e.* `assets` directory in sources. To access a resource, use the following path prefix: `assets/_kmviz_{plugin_name}_assets/`, ex: `assets/_kmviz_instance_plugin_assets/image.png`.

``` title="plugin structure"
kmviz_instance_plugin
├── kmviz_instance_plugin
│   ├── assets             <---
│   └── __init__.py
├── poetry.lock
├── pyproject.toml
└── README.md
```

