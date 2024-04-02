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

        Here is a condensed version of the documentation for a quickstart. For the complete documentation, please refer to the [wiki](https://github.com/tlemane/kmviz/wiki).

        ### Submit a query

        The configuration and submission of a query take place in the left sidebar. First, you have to choose one or more databases.

        1. Select one or more database

        Upon submitting a query, you will receive a notification containing a session ID, such as
        `kmviz-f47b1f69-6b6c-4209-b6fa-98d5f78bd9fd`. This ID can be used to reload your results at a later time which useful for queries that require long processing times.

        2.

        ### Result tabs

        **kmviz** allows to visualize results for each pair of database/query. At the top right, there a two selectors: the first one is to choose the database, and the second one is for the query. Query identifiers are the same as in your fasta/q input files.

        #### Index

        #### Table

        #### Map

        #### Plot

        #### Sequence


        """, mathjax=True),
        plugin_section,
        html.Div([
            *plugin_help
        ]),
    ], style = {"margin": 20})

    return res
