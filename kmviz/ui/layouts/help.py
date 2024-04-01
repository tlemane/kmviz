from dash_extensions.enrich import html, dcc
from kmviz.ui import state

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

    res = html.Div([
        dcc.Markdown("""
        ## Welcome to kmviz documentation!

        Here is a condensed version of the documentation for a quick start. For the complete documentation, please refer to [link](link).

        ### Submit a query

        ### Result tabs

        #### Index

        #### Table

        #### Map

        #### Sequence

        #### Plot

        """, mathjax=True),
        plugin_section,
        html.Div([
            *plugin_help
        ]),
    ], style = {"margin": 20})

    return res
