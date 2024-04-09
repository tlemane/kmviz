import dash_mantine_components as dmc
from dash_extensions.enrich import Input, Output, html, callback
from dash import no_update
from kmviz.ui.utils import prevent_update_on_empty, make_select_data, prevent_update_on_none, icons
from kmviz.ui.id_factory import kmviz_factory as kf
from kmviz.ui.components.store import ksfr
from kmviz.ui import state

kpsf = kf.child("select")
kgsf = kf.child("global-select")

from dash_iconify import DashIconify

def make_select_provider():
    res = html.Div([
        dmc.Divider(size="sm", color="gray", label="DATABASES", labelPosition="center"),
        dmc.MultiSelect(
            id=kpsf("provider"),
            label="Database(s)",
            data=make_select_data(state.kmstate.providers.list()),
            clearable=True,
            withAsterisk=True,
            icon=DashIconify(icon="fluent:library-16-regular"),
        )
    ])
    return res

def make_select_provider_callbacks():
    @callback(
        Input(kpsf("provider"), "value"),
        Output(ksfr("provider-active"), "data"),
        Output(kf("select-provider-config"), "data"),
        Output(kf("select-provider-config"), "value"),
        prevent_initial_callbacks=True,
    )
    def select_provider(providers):
        data = None
        active = []
        default = None

        if providers:
            active = providers
            data = make_select_data(providers)
            default = active[0]

        return active, data, default

def make_select():
    return dmc.Group([
        dmc.Switch(
            id=kf.sid("auto-apply"),
            offLabel=icons("autoff", width=20),
            onLabel=icons("auton", width=20),
            checked=True,
        ),
        dmc.Select(
            id=kgsf("provider"),
            placeholder="Select database",
            className="kmviz-gselect",
            size="xs"
        ),
        dmc.Select(
            id=kgsf("query"),
            placeholder="Select query",
            className="kmviz-gselect",
            size="xs"
        ),
    ], spacing=3, align="center", className="kmviz-gselect-group")

def make_select_callbacks():

    @callback(
        Input(kgsf("provider"), "value"),
        Output(kf.child("map").sid("select-preset"), "data"),
        Output(kf.child("plot").sid("select-preset"), "data"),
        Output(kf.child("map").sid("select-preset"), "style"),
        Output(kf.child("plot").sid("select-preset"), "style"),
    )
    def update_map_preset(value):
        if not value:
            return None, None, {"display": "none"}, {"display": "none"}

        if value.startswith("__kmviz_df"):
            prevent_update_on_none(None)

        p = state.kmstate.providers.get(value).presets

        map_data, map_style = None, {"display": "none"}
        plot_data, plot_style = None, {"display": "none"}
        if "map" in p:
            map_data = make_select_data(list(p["map"].keys()))
            map_style["display"] = "inline"
        if "plot" in p:
            plot_data = make_select_data(list(p["plot"].keys()))
            plot_style["display"] = "inline"

        return map_data, plot_data, map_style, plot_style

