from kmviz.core.plugin import KmVizPlugin, Provider
import dash_mantine_components as dmc
import random
from dash_extensions.enrich import html
from dash import dcc
from dash_iconify import DashIconify

class ExamplePlugin(KmVizPlugin):

    def is_instance_plugin(self) -> bool:
        return True

    def name(self):
        return "ExamplePlugin"

    def instance(self):

        layout = html.Div([
            dcc.Markdown("""
                ## Welcome to kmviz ORA instance.
                Here is an example of what happens when kmviz runs with 'instance' plugins.
                In addition to the usual plugin functions, an instance plugin provides a homepage that may describe
                the instance content and provide some help. Here we load the 'kmviz_ora' plugin.
                (Note that this is not a proposal for the new ORA design, just me discovering modern css 🙂)
            """
            ),
            html.Div([
                html.Div([
                    html.Img(src="assets/_kmviz_example_assets/water.webp", className="water"),
                    html.Div([
                        html.Img(src="assets/_kmviz_example_assets/ship.png")
                    ], className="ship"),
                ], className="ocean")
            ], className="hero"),
            html.A(
                dmc.Button(
                    "Go to dashboard",
                    leftIcon=DashIconify(icon="noto:rocket", width=20),
                    style={"position":"fixed", "top": "50%", "left":"50%"}),
                    href="/dashboard"
                ),
        ])


        return layout

    def external_styles(self):
        return [""]

    def help(self):
        res = dcc.Markdown("""
            ### ExamplePlugin documentation
        """
        )
        return res

kmviz_plugin = ExamplePlugin()

