from typing import Any
from kmviz.core.plugin import KmVizPlugin

from dash import dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash_extensions.enrich import html

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
            )
        ])

        return layout

kmviz_plugin = InstancePlugin()