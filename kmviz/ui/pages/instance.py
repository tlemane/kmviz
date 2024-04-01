from dash_extensions.enrich import (
    html,
    dcc,
)

import dash
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from kmviz.ui import state

def make_instance():

    plugin = state.kmstate.instance_plugin()

    if plugin:
        return plugin.instance()
    #layout = html.Div([
    #    dcc.Markdown("""
    #    ## Welcome to kmviz ORA instance.

    #    Here is an example of what happens when kmviz runs with 'instance' plugins. In addition to the usual plugin functions, an instance plugin provides a homepage that may describe the instance content and provide some help. Here we load the 'kmviz_ora' plugin.
    #    (Note that this is not a proposal for the new ORA design, just me discovering modern css 🙂)
    #    """),
    #    html.Div([
    #    html.Div([
    #        html.Img(src="assets/water.webp", className="water"),
    #        html.Div([
    #            html.Img(src="assets/ship.png")
    #        ], className="ship"),
    #    ], className="ocean")
    #], className="hero"),

    #html.A(dmc.Button("Go to dashboard", leftIcon=DashIconify(icon="noto:rocket", width=20), style={"position":"fixed", "top": "50%", "left":"50%"}), href="/dashboard"),
    #])


    #return layout

plugin = state.kmstate.instance_plugin()

if plugin:
    dash.register_page(__name__, path="/", name=plugin.name(), title=plugin.name())

layout = make_instance()
