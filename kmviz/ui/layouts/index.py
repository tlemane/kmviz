from dash_extensions.enrich import html, callback, Input, Output, dcc, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from kmviz.ui import state
import pandas as pd

import dash_ag_grid as dag

from kmviz.ui.components.grid import make_ag_grid
from kmviz.ui.utils import prevent_update_on_none
from kmviz.ui.id_factory import kmviz_factory as kf
from kmviz.ui.components.select import kgsf

kindex = kf.child("index")

def make_index_layout():
    res = html.Div([
        dmc.Center([
            html.H2("Index informations")
        ]),
        make_ag_grid(
            kindex.sid("infos-grid"),
            style = {"height": None},
            grid_opt = {"domLayout": "autoHeight"}
        ),
        dmc.Space(h=20),
        dmc.Button(
            "Export",
            id=kindex.sid("infos-button"),
            disabled=True,
            leftIcon=DashIconify(icon="ph:export", width=20)
        ),
        dmc.Center([
            html.H2("Index metadata")
        ]),

        make_ag_grid(kindex.sid("metadata-grid")),
        dmc.Space(h=20),
        dmc.Group([
            dmc.Button(
                "Export",
                id=kindex.sid("metadata-button"),
                disabled=True,
                leftIcon=DashIconify(icon="ph:export", width=20)
            ),
            dmc.Button(
                "Remove filters",
                id=kindex.sid("metadata-rmf"),
                disabled=True,
                leftIcon=DashIconify(icon="ph:trash", width=20)
            ),
        ])
    ])

    return res

def make_index_layout_callbacks():

    @callback(
        Input(kindex.sid("metadata-rmf"), "n_clicks"),
        Output(kindex.sid("metadata-grid"), "filterModel"),
        prevent_initial_callbacks=True
    )
    def remove_metadata_table_filters(n_clicks):
        if n_clicks:
            return {}
        prevent_update_on_none(None)

    @callback(
        Input(kindex.sid("metadata-button"), "n_clicks"),
        Output(kindex.sid("metadata-grid"), "exportDataAsCsv")
    )
    def export_metadata(n_clicks):
        if n_clicks:
            return True
        prevent_update_on_none(None)

    @callback(
        Input(kindex.sid("infos-button"), "n_clicks"),
        Output(kindex.sid("infos-grid"), "exportDataAsCsv")
    )
    def export_metadata(n_clicks):
        if n_clicks:
            return True
        prevent_update_on_none(None)

    @callback(
        Input(kgsf("provider"), "value"),
        Output(kindex.sid("infos-button"), "disabled"),
        Output(kindex.sid("metadata-button"), "disabled"),
        Output(kindex.sid("metadata-rmf"), "disabled"),
        prevent_initial_callbacks=True
    )
    def enable_index_table_buttons(provider):
        prevent_update_on_none(provider)
        return False, False, False

    @callback(
        Input(kgsf("provider"), "value"),
        Output(kindex.sid("infos-grid"), "rowData"),
        Output(kindex.sid("infos-grid"), "columnDefs"),
        Output(kindex.sid("metadata-grid"), "rowData"),
        Output(kindex.sid("metadata-grid"), "columnDefs"),
        prevent_initial_callbacks=True
    )
    def update_index_table(provider):
        if provider == "__kmviz_df":
            prevent_update_on_none(None)

        p = state.kmstate.providers.get(provider)

        infos_rd = p.infos_df.to_dict("records")
        infos_f = [{"field": f} for f in list(p.infos_df)]

        meta_rd = p.db.df().to_dict("records")
        meta_f = [{"field": f} for f in list(p.db.df())]

        return infos_rd, infos_f, meta_rd, meta_f

