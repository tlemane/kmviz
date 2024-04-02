from dash_extensions.enrich import html, dcc
from kmviz.ui import state
import dash

from importlib_resources import files

def make_help_layout():

    plugin_help = []
    for _, plugin in state.kmstate.plugins.items():
        if h := plugin.help():
            plugin_help.append(h)

    plugin_section = html.Div()

    if state.kmstate.plugins:
        plugin_section = dcc.Markdown("""
        ---

        ## Plugins

        This instance has loaded one or more plugins. If these provide help, you will find it below.
        """)

    help_md = ""

    with open(files("kmviz").joinpath("assets/help.md"), "r") as doc:
        help_md = doc.read()

    res = html.Div([
        dcc.Markdown(help_md, mathjax=True),
        plugin_section,
        html.Div([
            *plugin_help
        ]),
    ], style = {"margin": 20})

    return res
