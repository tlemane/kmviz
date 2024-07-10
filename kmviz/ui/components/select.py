import dash_mantine_components as dmc
from dash_extensions.enrich import Input, Output, State, html, callback, dcc
from dash import no_update
from kmviz.ui.utils import prevent_update_on_empty, make_select_data, prevent_update_on_none, icons
from kmviz.ui.id_factory import kmviz_factory as kf
from kmviz.ui.components.store import ksfr, ksf
from kmviz.ui import state
import orjson
from flask import jsonify
from dataclasses import dataclass
from kmviz.core.query import QueryResponseGeo
from typing import Dict

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
            value=state.kmstate.defaults["databases"],
        )
    ], style = {"display": "none" if state.kmstate.defaults["hide_db"] else "inline"})
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
        dmc.ActionIcon(
            DashIconify(icon="bi:filetype-json", width=20),
            id=kf.sid("download-all-results-btn"),
            variant="filled",
            color = "#1C7ED6",
        ),
        dmc.Space(w=10),
        dcc.Download(id=kf.sid("download-all-results")),
        dmc.Switch(
            id=kf.sid("auto-apply"),
            offLabel=icons("autoff", width=20),
            onLabel=icons("auton", width=20),
            checked=True,
        ),
        dmc.Space(w=10),
        dmc.Select(
            id=kgsf("provider"),
            placeholder="Select database",
            icon=DashIconify(icon="fluent:library-16-regular"),
            className="kmviz-gselect",
            size="xs"
        ),
        dmc.Select(
            id=kgsf("query"),
            placeholder="Select query",
            icon=DashIconify(icon="mdi:dna"),
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

        prevent_update_on_empty(state.kmstate.providers.list())

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

    @callback(
        Input(kf.sid("download-all-results-btn"), "n_clicks"),
        State(ksf("query-results"), "data"),
        Output(kf.sid("download-all-results"), "data")
    )
    def download_all(n_clicks, data):
        if n_clicks and len(data) and state.kmstate.providers.list():
            for qname, res in data.items():
                for name in res:
                    R = QueryResponseGeo(
                        res[name]._query,
                        res[name]._response,
                        orjson.loads(res[name].df.to_json()),
                        state.kmstate.providers.get(name).db.geodata
                    )
                    res[name] = R

            return dict(content=orjson.dumps(jsonify(data).json).decode(), filename=f"session.json")

        prevent_update_on_none(None)