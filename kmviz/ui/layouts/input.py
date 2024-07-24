from dash_extensions.enrich import html, Input, State, Output, callback, clientside_callback, Serverside, no_update, ClientsideFunction
from dash import Patch

from kmviz.ui.utils import prevent_update_on_none, make_select_data
from kmviz.ui.components.factory import ComponentFactory as cf
from kmviz.ui.components.factory import km_color, kshow, khide
from kmviz.ui.components.helpers import load_file_content
from kmviz.ui.id_factory import kid
from kmviz.core.config import state
from kmviz.core.io import KmVizIOError, parse_fastx
from kmviz.core.query import Query


import dash_mantine_components as dmc
from dash_iconify import DashIconify

class SideDBLayout:
    def __init__(self, st: state):
        self.st = st

    def layout(self) -> html.Div:
        return cf.div(
            kid.input["db-div"],
            cf.multi(
                kid.input("db"),
                data=self.st.engine.list(),
                label="Database(s)",
                clearable=True,
                withAsterisk=True,
                leftSection=DashIconify(icon="fluent:library-16-regular"),
                value=self.st.defaults.database,
            ),
            dmc.Space(h=10),
            style = khide if self.st.defaults.hide else kshow
        )

    def callbacks(self) -> None:

        @callback(
            Input(kid.input("db"), "value"),
            Output(kid.store("databases"), "data"),
            Output(kid.config["select"], "data"),
            Output(kid.config["select"], "value"),
            prevent_initial_call=True
        )
        def select_database(db_names):
            if db_names:
                return db_names, make_select_data(db_names), db_names[0]
            return [], [], None

class SideInputLayout:
    def __init__(self, st: state):
        self.st = st
        kid.register(kid.side.new("input"), "input")

    def _file_layout(self) -> html.Div:
        return cf.div(
            kid.input["file-div"],
            cf.upload(
                kid.input("file"),
                cf.button(kid.input["file-button"], "Upload FASTA/Q file", size="sm", fullWidth=True)
            ),
            style=khide
        )

    def _session_layout(self) -> html.Div:
        return cf.div(
            kid.input["session-div"],
            cf.text(kid.input("session"), required=True, label="Session ID", placeholder="kmviz-324bfabc-50e7-44ac-89d9-6460803d2f5e"),
            dmc.Space(h=2),
            cf.button(kid.input["session-button"], "Load", size="sm", fullWidth=True),
            style=khide
        )

    def _text_layout(self) -> html.Div:
        return cf.div(
            kid.input["text-div"],
            cf.area(
                kid.input("text"),
                label="Query sequence(s)",
                description="Fasta/Fastq format",
                placeholder=">Query\nACCGTAGCCTTAGAATTA",
                spellCheck=False,
                autosize=True,
                maxRows=4,
                required=True
            ),
            cf.button(kid.input["text-button"], "Load", size="xs", fullWidth=True),
            style=kshow
        )

    def layout(self) -> html.Div:
        return cf.div(
            kid.input["div"],
            cf.divider(size="sm", color="gray", label="INPUT", labelPosition="center"),
            cf.div(
                kid.input["input-div"],
                dmc.Space(h=5),
                cf.segmented(
                    kid.input["select"],
                    data=["text", "file", "session"],
                    orientation="horizontal",
                    size="sm",
                    fullWidth=True,
                    color=km_color,
                    value="text"
                ),
                dmc.Space(h=10),
                cf.div(
                    kid.input["placeholder"],
                    self._text_layout(),
                    self._file_layout(),
                    self._session_layout(),
                )
            ),
            cf.div(kid.input["error"]),
            dmc.Space(h=10)
        )

    def _text_callbacks(self) -> None:
        @callback(
            Input(kid.input["text-button"], "n_clicks"),
            State(kid.input("text"), "value"),
            Output(kid.store("sequences"), "data"),
            Output(kid.input("text"), "error"),
            Output(kid.input["input-div"], "style"),
            Output(kid.input["error"], "children"),
            prevent_initial_call=True
        )
        def load_from_text(n_clicks, content):
            if n_clicks:
                try:
                    queries = [Query(name, seq) for name, seq, _ in parse_fastx(content, self.st.limits)]
                    query = "queries" if len(queries) > 1 else "query"
                    message = dmc.Text(f"🗎 Input: {len(queries)} {query}", fw=500)
                    return Serverside(queries), no_update, khide, message
                except KmVizIOError as e:
                    return no_update, dmc.Text(str(e), fw=500, color="red"), no_update, no_update
            return no_update, no_update, no_update, no_update

    def _file_callbacks(self) -> None:
        @callback(
            Input(kid.input("file"), "filename"),
            State(kid.input("file"), "contents"),
            Output(kid.store("sequences"), "data"),
            Output(kid.input["input-div"], "style"),
            Output(kid.input["error"], "children"),
            Output(kid.input("file"), "filename"),
            prevent_initial_call=True
        )
        def load_from_file(filename, contents):
            if contents:
                content = load_file_content(filename, contents, "utf-8")
                try:
                    queries = [Query(name, seq) for name, seq, _ in parse_fastx(content, self.st.limits)]
                    query = "queries" if len(queries) > 1 else "query"
                    message = dmc.Text(f"🗎 {filename}: {len(queries)} {query}", fw=500)
                    return Serverside(queries), khide, message, None
                except KmVizIOError as e:
                    return no_update, no_update, dmc.Text(str(e), fw=500, color="red"), None
            return (no_update,) * 4

    def _session_callbacks(self) -> None:
        @callback(
            Input(kid.input["session-button"], "n_clicks"),
            State(kid.input("session"), "value"),
            Output(kid.store["results"], "data"),
            Output(kid.kmviz("database"), "data"),
            Output(kid.kmviz("database"), "value"),
            Output(kid.kmviz("query"), "data"),
            Output(kid.kmviz("query"), "value"),
            Output(kid.input("session"), "error"),
            Output(kid.store["session-id"], "data"),
            Output(kid.kmviz["side-layout"], "style"),
            Output(kid.kmviz["main-layout"], "style"),

            Output(kid.tabs["index"], "disabled"),
            Output(kid.tabs["table"], "disabled"),
            Output(kid.tabs["map"], "disabled"),
            Output(kid.tabs["plot"], "disabled"),
            Output(kid.tabs["sequence"], "disabled"),
            Output(kid.tabs["tabs"], "value"),

            prevent_initial_call=True
        )
        def load_session(n_clicks, session_id):
            if n_clicks:
                try:
                    res = self.st.get(session_id)
                    return (Serverside(res[0]), res[1], res[2], res[3], res[4], no_update, session_id, khide, {"padding-left": "10px"}) + (False,) * 5 + ("table",)
                except:
                    msg = "Session not found. Invalid session id, query still running, or results erased."
                    return (no_update,) * 5 + (msg, None) + (no_update,) * 8
            return (no_update,) * 8

    def callbacks(self) -> None:
        self._text_callbacks()
        self._file_callbacks()
        self._session_callbacks()

        clientside_callback(
            """
            function(value) {
                if (value === "text") {
                    return [{ 'display' : 'inline'}, { 'display' : 'none'}, { 'display' : 'none'}];
                } else if (value === "session") {
                    return [{ 'display' : 'none'}, { 'display' : 'inline'}, { 'display' : 'none'}];
                } else {
                    return [{ 'display' : 'none'}, { 'display' : 'none'}, { 'display' : 'inline'}];
                }
            }
            """,
            Input(kid.input["select"], "value"),
            Output(kid.input["text-div"], "style"),
            Output(kid.input["session-div"], "style"),
            Output(kid.input["file-div"], "style"),
            prevent_initial_call=True
        )
