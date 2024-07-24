from kmviz.core.config import state
from kmviz.ui.components.factory import ComponentFactory as cf
from kmviz.ui.components.factory import km_color, khide
from kmviz.ui.id_factory import kid
from kmviz.ui.utils import make_select_data
from kmviz.ui.components.helpers import load_file_content
from dash_extensions.enrich import Input, Output, callback, Serverside, html, no_update
from kmviz.core.query import Query, Response, QueryResponse
import dash_mantine_components as dmc


import pandas as pd
from dash_iconify import DashIconify
import base64
import orjson

class SessionLayout:
    def __init__(self, st: state, factory):
        self.st = state
        self.f = factory

    def layout(self):
        return cf.div(
            self.f["div"],
            cf.upload(
                self.f["session-file"],
                cf.button(
                    self.f["session-button"],
                    "Upload Session",
                    size="xs",
                    color=km_color,
                    leftSection=DashIconify(icon="bi:filetype-json", width=20),
                    className="kmviz-session-button"
                )
            ),
            cf.div(self.f["session-error"])
        )

    def callbacks(self):
        @callback(
            Input(self.f["session-file"], "filename"),
            Input(self.f["session-file"], "contents"),
            Output(kid.store["results"], "data"),
            Output(kid.pom["store"], "data"),
            Output(kid.kmviz("database"), "data"),
            Output(kid.kmviz("database"), "value"),
            Output(kid.kmviz("query"), "data"),
            Output(kid.kmviz("query"), "value"),
            Output(self.f["session-error"], "children"),
            Output(self.f["session-file"], "filename"),
            prevent_initial_call=True,
        )
        def input_session_file(filename, contents):
            try:
                content = load_file_content(filename, contents, "utf-8")
                session = orjson.loads(content)

                result = {}
                providers = []
                queries = []
                geo = {}

                session_id = list(session.keys())[0]
                session = session[session_id]
                for query, pres in session.items():
                    queries.append(query)
                    for provider, res in pres.items():
                        providers.append(provider)
                        q = Query(res["_query"]["_name"], res["_query"]["_seq"])
                        m = pd.DataFrame.from_dict(res["_metadata"])
                        m.insert(0, "ID", m.pop("ID"))
                        geo[provider] = res["_geodata"]
                        responses = {}
                        for sample, rep in res["_response"].items():
                            responses[sample] = Response(**rep)
                        result[query] = {provider: QueryResponse(q, responses, m)}
                pdata = make_select_data(providers)
                qdata = make_select_data(queries)

                return Serverside(result), {"session": geo}, pdata, providers[0], qdata, queries[0], [], None

            except Exception as e:
                msg = html.Div([dmc.Text("An error occured while loading your session file", color="red", weight=500)], className="kmviz-session-error")
                return (no_update,) * 6 + (msg, None)