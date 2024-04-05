from dash_extensions.enrich import (
    dcc,
    html,
    DashBlueprint,
    LogTransform,
    NoOutputTransform,
    ServersideOutputTransform
)

import dash
import dash_mantine_components as dmc

from kmviz.ui import state
from kmviz.ui.id_factory import kmviz_factory as kf
from kmviz.ui.components.store import make_stores, make_stores_callbacks
from kmviz.ui.components.select import make_select, make_select_callbacks
from kmviz.ui.layouts.sidebar import make_sidebar_layout, make_sidebar_layout_callbacks
from kmviz.ui.layouts.tabs import make_tabs
import uuid

def make_dashboard():

    layout = html.Div([
        dcc.Store(kf.sid("session-id")),
        make_stores(),
        make_select(),
        dmc.Grid([
            dmc.Col(make_sidebar_layout(), id=kf.sid("sidebar-layout"), span="content"),
            dmc.Col(make_tabs(), id=kf.sid("tabs-layout"), span="auto")
        ])
    ])

    make_stores_callbacks()
    make_select_callbacks()
    make_sidebar_layout_callbacks()

    return layout
    #return dashboard

dash.register_page(__name__, path=state.kmstate.dashboard_path, name="dashboard", title="dashboard")

layout = make_dashboard()
