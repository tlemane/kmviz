from kmviz.core.config import state
from kmviz.ui.id_factory import kid
from kmviz.ui.components.factory import ComponentFactory as cf
from dash_extensions.enrich import callback, Input, State, Output, no_update, clientside_callback
from dash.exceptions import PreventUpdate
from kmviz.ui.utils import prevent_update_on_none
import dash_mantine_components as dmc
import kmviz.core.config as kconf

from dash_iconify import DashIconify

class Index:
    def __init__(self, st: state):
        self.st = st

    def layout(self):
        return cf.div(
            kid.index["div"],
            dmc.Center(cf.h2("Index information")),
            cf.ag_grid(
                kid.index("info-grid"),
                grid_opt = {"domLayout": "autoHeight"}
            ),
            dmc.Space(h=20),
            cf.button(
                kid.index["info-export"],
                "Export",
                disabled=True,
                leftSection=DashIconify(icon="ph:export", width=20)
            ),
            dmc.Center(cf.h2("Index metadata")),
            cf.ag_grid(
                kid.index("meta-grid")
            ),
            dmc.Space(h=20),
            cf.group(
                kid.index["grp-btn"],
                cf.button(
                    kid.index["meta-export"],
                    "Export",
                    disabled=True,
                    leftSection=DashIconify(icon="ph:export", width=20)
                ),
                cf.button(
                    kid.index["meta-rmf"],
                    "Remove filters",
                    disabled=True,
                    leftSection=DashIconify(icon="ph:trash", width=20)
                )
            )
        )

    def callbacks(self) -> None:

        clientside_callback(
            """
            function(n_clicks) {
                if (n_clicks) {
                    return {};
                }
                return window.dash_clientside.no_update;
            }
            """,
            Input(kid.index["meta-rmf"], "n_clicks"),
            Output(kid.index("meta-grid"), "filterModel"),
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
            Input(kid.index["meta-export"], "n_clicks"),
            Output(kid.index("meta-grid"), "exportDataAsCsv"),
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
            Input(kid.index["info-export"], "n_clicks"),
            Output(kid.index("info-grid"), "exportDataAsCsv"),
            prevent_initial_call=True
        )

        clientside_callback(
            """
            function(database) {
                if (!database) {
                    return [window.dash_clientside.no_update, window.dash_clientside.no_update, window.dash_clientside.no_update];
                }
                return [false, false, false];
            }
            """,
            Input(kid.kmviz("database"), "value"),
            Output(kid.index["info-export"], "disabled"),
            Output(kid.index["meta-export"], "disabled"),
            Output(kid.index["meta-rmf"], "disabled"),
            prevent_initial_call=True
        )

        @callback(
            Input(kid.kmviz("database"), "value"),
            Output(kid.index("info-grid"), "rowData"),
            Output(kid.index("info-grid"), "columnDefs"),
            Output(kid.index("meta-grid"), "rowData"),
            Output(kid.index("meta-grid"), "columnDefs"),
            prevent_initial_call=True
        )
        def update_index_table(db):
            if db == "__kmviz_df":
                raise PreventUpdate

            p = kconf.st.engine.get(db)

            idf = p.infos_df
            infos_rd = idf.to_dict("records")
            infos_f = [{"field": f} for f in list(idf)]

            df = p.db.df()
            meta_rd = df.to_dict("records")
            meta_f = [{"field": f} for f in list(df)]

            return infos_rd, infos_f, meta_rd, meta_f