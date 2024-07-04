from dash_extensions.enrich import (
    html,
    dcc,
)

import dash
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from kmviz.ui import state

def make_instance(plugin):
    if plugin:
        return plugin.instance()

plugin = state.kmstate.instance_plugin()

if plugin:
    dash.register_page(__name__, path="/", name=plugin.name(), title=plugin.name())

layout = make_instance(plugin)
