from dash_extensions.enrich import html, dash_table, Input, Output, dcc, State, callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify

import dash_ag_grid as dag
from dash import Patch
from kmviz.ui import state
import pandas as pd

from kmviz.ui.components.grid import make_ag_grid
from kmviz.ui.id_factory import kmviz_factory as kf
from kmviz.ui.utils import prevent_update_on_none
from kmviz.ui.components.select import kgsf
from kmviz.ui.components.store import ksf

from pandas.api.types import is_numeric_dtype, is_datetime64_dtype

ktable = kf.child("table")

def make_table_layout():
    res = html.Div([
        dmc.Space(h=5),
        make_ag_grid(ktable.sid("grid"), {}, {}, {}, style = {"height": "85vh"}),
        dmc.Space(h=5),
        dmc.Group([
            dmc.Button(
                "Export",
                id=ktable.sid("button"),
                disabled=True,
                leftIcon=DashIconify(icon="ph:export", width=20)
            ),
            dmc.Button(
                "Remove filters",
                id=ktable.sid("rmf"),
                disabled=True,
                leftIcon=DashIconify(icon="ph:trash", width=20)
            ),
            dmc.Button(
                "Filter NaN",
                id=ktable.sid("nan"),
                disabled=True,
                leftIcon=DashIconify(icon="mingcute:na-fill", width=20)
            )
        ])
    ])

    return res

def make_table_layout_callbacks():

    @callback(
        Input(kgsf("query"), "value"),
        State(kgsf("provider"), "value"),
        State(ksf("query-results"), "data"),
        Output(ktable.sid("grid"), "rowData"),
        Output(ktable.sid("grid"), "columnDefs"),
        Output(ktable.sid("panel"), "disabled"),
        prevent_initial_callbacks=True,
    )
    def update_table_grid(query, provider, query_result):

        def column_filter(data):
            if is_numeric_dtype(data):
                return "agNumberColumnFilter"
            if is_datetime64_dtype(data):
                return "agDateColumnFilter"
            return "agTextColumnFilter"

        fields = [
            {
                "field": x,
                "filterParams": {"maxNumConditions": 10000},
                "suppressMenu": False,
                "filter": column_filter(query_result[query][provider].df[x])
            }
            for x in list(query_result[query][provider].df)
        ]

        return query_result[query][provider].df.to_dict("records"), fields, False

    @callback(
        Input(ktable.sid("button"), "n_clicks"),
        Output(ktable.sid("grid"), "exportDataAsCsv"),
        prevent_initial_callbacks=True,
    )
    def download_table_as_csv(n_clicks):
        if n_clicks:
            return True
        prevent_update_on_none(None)

    @callback(
        Input(kgsf("query"), "value"),
        State(kgsf("provider"), "value"),
        Output(ktable.sid("button"), "disabled"),
        Output(ktable.sid("rmf"), "disabled"),
        Output(ktable.sid("nan"), "disabled"),
        prevent_initial_callbacks=True,
    )
    def enable_table_grid_buttons(query, provider):
        prevent_update_on_none(query, provider)
        return False, False, False

    @callback(
        Input(ktable.sid("rmf"), "n_clicks"),
        Output(ktable.sid("grid"), "filterModel")
    )
    def remove_table_filters(n_clicks):
        if n_clicks:
            return {}
        prevent_update_on_none(None)

    @callback(
        Input(ktable.sid("nan"), "n_clicks"),
        State(ktable.sid("grid"), "columnDefs"),
        Output(ktable.sid("grid"), "filterModel", allow_duplicate=True),
    )
    def filter_nan(n_clicks, fields):
        if n_clicks:
            cols = [x["field"] for x in fields]
            p = Patch()
            for c in cols[1:]:
                p[c] = {'filterType': 'text', 'type': 'notBlank', 'filter': ''}
            return p



