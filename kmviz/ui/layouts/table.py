from kmviz.core.config import state
from dash_extensions.enrich import html, Input, State, callback, Output, no_update, clientside_callback
from kmviz.ui.components.factory import ComponentFactory as cf
from kmviz.ui.components.factory import km_color
from kmviz.ui.id_factory import kid
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from kmviz.ui.utils import prevent_update_on_none
from dash.exceptions import PreventUpdate
from dash import Patch
import duckdb
import pandas as pd
from pandas.api.types import is_numeric_dtype, is_datetime64_dtype
from kmviz.ui.layouts.filter import FilterLayout
import uuid

class TableLayout:
    def __init__(self, st: state):
        self.st = st
        self._filter = FilterLayout(kid.table, kid.table("grid"))

    def layout(self) -> html.Div:
        return cf.div(
            kid.table["div"],
            dmc.Space(h=5),
            self._filter.layout(),
            dmc.Space(h=5),
            cf.ag_grid(kid.table("grid"), {}, {}, {}, style = {"height": "80vh"}),
            dmc.Space(h=5),
            cf.group(
                kid.table["grp-button"],
                cf.button(
                    kid.table["export-button"],
                    "Export",
                    disabled=True,
                    leftSection=DashIconify(icon="ph:export", width=20)
                ),
                cf.button(
                    kid.table["rmf-button"],
                    "Remove filters",
                    disabled=True,
                    leftSection=DashIconify(icon="ph:trash", width=20)
                ),
                cf.button(
                    kid.table["filter-button"],
                    "Filter NaN",
                    disabled=True,
                    leftSection=DashIconify(icon="mingcute:na-fill", width=20)
                )
            ),
        )

    def callbacks(self) -> None:
        clientside_callback(
            """
            function(database, query) {
                if (!database || !query) {
                    return [window.dash_clientside.no_update, window.dash_clientside.no_update, window.dash_clientside.no_update];
                }
                return [false, false, false];
            }
            """,
            Input(kid.kmviz("query"), "value"),
            State(kid.kmviz("database"), "value"),
            Output(kid.table["filter-button"], "disabled"),
            Output(kid.table["export-button"], "disabled"),
            Output(kid.table["rmf-button"], "disabled"),
            prevent_initial_call=True
        )

        clientside_callback(
            """
            function(n_clicks) {
                if (n_clicks) {
                    return {};
                }
                return window.dash_clientside.no_update;
            }
            """,
            Input(kid.table["rmf-button"], "n_clicks"),
            Output(kid.table("grid"), "filterModel"),
            prevent_initial_call=True
        )

        clientside_callback(
            """
            function(n_clicks) {
                if (n_clicks) {
                    return true;
                }
                return window.dash_clientside.no_update;
            }
            """,
            Input(kid.table["export-button"], "n_clicks"),
            Output(kid.table("grid"), "exportDataAsCsv"),
            prevent_initial_call=True
        )

        @callback(
            Input(kid.table["filter-button"], "n_clicks"),
            State(kid.table("grid"), "columnDefs"),
            Output(kid.table("grid"), "filterModel", allow_duplicate=True),
            prevent_initial_call=True
        )
        def filter_nan(n_clicks, fields):
            if n_clicks:
                cols = [x["field"] for x in fields]
                p = Patch()
                for c in cols[1:]:
                    p[c] = {'filterType': 'text', 'type': 'notBlank', 'filter': ''}
                return p

        @callback(
            Input(kid.kmviz("query"), "value"),
            Input(kid.pom["store"], "data"),
            State(kid.kmviz("database"), "value"),
            State(kid.store["results"], "data"),
            Output(kid.table("grid"), "rowData"),
            Output(kid.table("grid"), "columnDefs"),
            prevent_initial_call=True
        )
        def update_grid(query, plot_only, db, results):

            def colf(data):
                if is_numeric_dtype(data):
                    return "agNumberColumnFilter"
                if is_datetime64_dtype(data):
                    return "agDateColumnFilter"
                return "agTextColumnFilter"


            if "df" not in plot_only:
                df = results[query][db].df
            else:
                df = plot_only["df"]

            fields = [
                {
                    "field": x,
                    "filterParams": {"maxNumConditions": 10000},
                    "suppressMenu": True,
                    "filter": colf(df[x]),
                    "cellRenderer": self.st.ui.crs[x][0] if x in self.st.ui.crs else "",
                    "cellRendererParams": self.st.ui.crs[x][1] if x in self.st.ui.crs else ""
                } for x in list(df)
            ]

            return df.to_dict("records"), fields

        self._filter.callbacks()