from kmviz.ui.components.factory import ComponentFactory as cf
from kmviz.ui.components.factory import km_color
from dash_iconify import DashIconify
from dash_extensions.enrich import no_update, State, Input, Output, callback, clientside_callback
from dash_extensions import Keyboard
import pandas as pd
import duckdb
from dash import Patch
import dash_mantine_components as dmc

class FilterLayout:
    def __init__(self, factory, data):
        self.f = factory
        self.data = data

    def layout(self):
        c = [
            Keyboard(
                cf.text(
                    self.f("sql-query"),
                    placeholder="Temperature > 26 AND Season = 'Spring'",
                    size="xs"),
                captureKeys=["Enter"],
                id=self.f["keyboard"],
                className="kmviz-filter-keyboard"
            ),
            cf.action(self.f["sql-query-button"], DashIconify(icon="carbon:play-outline", width=30), variant="filled", color=km_color),
            cf.action(self.f["rmf"], DashIconify(icon="lucide:filter-x", width=20), variant="filled", color=km_color),
        ]

        return cf.group(
            self.f["grp-filter"],
            *c,
            gap=3
        )

    def callbacks(self):
        clientside_callback(
            """
            function(n_clicks) {
                if (n_clicks) {
                    return [{}, ""];
                }
                return [window.dash_clientside.no_update, window.dash_clientside.no_update];
            }
            """,
            Input(self.f["rmf"], "n_clicks"),
            Output(self.data, "filterModel"),
            Output(self.f("sql-query"), "value"),
            prevent_initial_call=True
        )

        @callback(
            Input(self.f["sql-query-button"], "n_clicks"),
            Input(self.f["keyboard"], "n_keydowns"),
            State(self.f("sql-query"), "value"),
            State(self.data, "rowData"),
            Output(self.data, "filterModel"),
            Output(self.f("sql-query"), "error"),
            prevent_initial_call=True
        )
        def df_query(n_clicks, n_keydowns, query, data):
            if n_clicks or n_keydowns:
                df = pd.DataFrame.from_dict(data)
                try:
                    if not query:
                        return {}, None

                    f = duckdb.sql(f"select ID from df WHERE {query}").df()
                    ids = list(f["ID"])
                    cond = []

                    for i in ids:
                        cond.append(
                            {"filter": i, "filterType":"text", "type":"equals"}
                        )

                    if not ids:
                        cond.append(
                            {"filter": " ", "filterType":"text", "type":"equals"}
                        )

                    p = Patch()
                    p["ID"] = { "filterType": "text", "operator": "OR", "conditions": cond}
                    return p, None
                except Exception as e:
                    return no_update, dmc.Text(str(e), color="red")
            return (no_update,) * 2