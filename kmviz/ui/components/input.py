import base64

from dash import Patch, no_update
import dash_mantine_components as dmc
from dash_extensions.enrich import Input, Output, State, html, dcc, Serverside, callback

from kmviz.ui.id_factory import kmviz_factory as kf
from kmviz.ui.patch import style_hide_patch, style_inline_patch
from kmviz.ui.components.store import ksfr
from kmviz.ui.utils import prevent_update_on_none

from kmviz.core.query import Query, QueryResponse, Response
from kmviz.core.io import parse_fastx, KmVizIOError
from kmviz.ui import state
from kmviz.ui.utils import make_select_data
from kmviz.ui.components.store import ksf
from kmviz.ui.components.select import kgsf
from dataclasses import dataclass
from dash_iconify import DashIconify

from io import StringIO
import pandas as pd
import orjson

kif = kf.child("input")
kidf = kif.child("div")

KMVIZ_UPLOAD_STYLE = {
    'width': '80%%',
    'height': '40px',
    'lineHeight': '40px',
    'borderWidth': '1px',
    'borderStyle': 'dashed',
    'borderRadius': '5px',
    'textAlign': 'center',
    'margin': '10px',
    'align': 'center',
    'display': 'inherit'
}

def make_input_session():
    return [
        dmc.TextInput(
            id=kif("session"),
            required=True,
            label="Session ID",
            placeholder="kmviz-324bfabc-50e7-44ac-89d9-6460803d2f5e"
        ),
        dmc.Space(h=5),
        html.Div(id=kif("session-error")),
        dmc.Button("Load", id=kif("session-load"), style={"display":"inline"})
    ]

def make_input_session_callbacks():
    @callback(
        Input(kif("session-load"), "n_clicks"),
        State(kif("session"), "value"),
        Output(ksf("query-results"), "data"),
        Output(kgsf("provider"), "data"),
        Output(kgsf("provider"), "value"),
        Output(kgsf("query"), "data"),
        Output(kgsf("query"), "value"),
        Output(kf.sid("sidebar-layout"), "style"),
        Output(kif("session"), "error"),
        Output(kf.sid("session-id"), "data"),
        prevent_initial_callbacks=True,
        prevent_initial_call=True,
    )
    def load_session(n_clicks, session_id):
        if n_clicks:
            try:
                res = state.kmstate.get_result(session_id)
                return Serverside(res[0]), res[1], res[2], res[3], res[4], {"display":"none"}, no_update, session_id
            except:
                msg = "Session not found. Invalid session id, query still running, or results erased."
                return no_update, no_update, no_update, no_update, no_update, no_update, msg, None
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, None

def make_input_dataframe():
    return [
        dcc.Upload(
            id=kif("dataframe"),
            children=["Drop or ", html.A("Select a file")],
            style = KMVIZ_UPLOAD_STYLE
        ),
        html.Div(id=kif("dataframe-error"))
    ]

@dataclass
class _df_wrap:
    df: pd.DataFrame

def make_input_dataframe_callbacks():

    @callback(
        Input(kif("dataframe"), "filename"),
        Input(kif("dataframe"), "contents"),
        Output(ksf("query-results"), "data"),
        Output(kif("dataframe-error"), "children"),
        Output(kf.sid("sidebar-layout"), "style"),
        Output(kf.sid("index-panel"), "style"),
        Output(kf.sid("seq-panel"), "style"),
        Output(kgsf("provider"), "value"),
        Output(kgsf("query"), "value"),
        Output(kgsf("provider"), "style"),
        Output(kgsf("query"), "style"),
        Output("tab-select", "value"),
        prevent_initial_call=True,
    )
    def load_input_from_file(filename, contents):

        hide = {"display": "none"}

        prevent_update_on_none(filename, contents)

        content_type, data = contents.split(",")
        content = base64.b64decode(data).decode()

        try:
            df = None
            pdio = StringIO(content)
            if filename.endswith("csv") or filename.endswith("tsv"):
                try:
                    df = pd.read_csv(pdio, sep="\t")
                except:
                    raise KmVizIOError(f"Error while loading '{filename}'")

            key = "__kmviz_df_nogeo"
            if "Latitude" in df and "Longitude" in df:
                key = "__kmviz_df"

            res = {}
            res[key] = {}
            res[key][key] = _df_wrap(df)

            return Serverside(res), no_update, hide, hide, hide, key, key, hide, hide, "table"

        except KmVizIOError as e:
            message = dmc.Text(str(e), color="red", weight=500)
            return Serverside([]), message, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update


def make_input_text():
    return [
        dmc.Textarea(
            id=kif("text"),
            label="Query sequence(s)",
            description="Fasta/Fastq format",
            placeholder=">Query\nACCGTAGCCTTAGAATTA",
            spellCheck=False,
            autosize=True,
            maxRows=4,
            required=True,
            style={"display":"inline"}
        ),
        dmc.Space(h=5),
        html.Div(id=kif("text-msg")),
        dmc.Button("Load", id=kif("text-load"), style={"display":"inline"})
    ]

def make_input_text_callbacks():

    @callback(
        Input(kif("text-load"), "n_clicks"),
        State(kif("text"), "value"),
        Output(ksfr("query-sequences"), "data"),
        Output(kif("text-load"), "style"),
        Output(kif("text"), "error"),
        Output(kif("text-msg"), "children"),
        Output(kif("select"), "style"),
        Output(kif("text"), "style"),
        prevent_initial_call=True,
    )
    def load_input_from_text(n_clicks, content):
        if n_clicks:
            try:
                queries = [Query(name, seq) for name, seq, _ in parse_fastx(content, state.kmstate.limits)]
                query = "queries" if len(queries) > 1 else "query"
                message = dmc.Text(f"🗎 raw ({len(queries)} {query})", weight=500)
                return Serverside(queries), style_hide_patch(), None, message, style_hide_patch(), style_hide_patch()
            except KmVizIOError as e:
                return Serverside([]), Patch(), str(e), None, no_update, no_update
        return no_update, no_update, no_update, no_update, no_update, no_update

    @callback(
        Input(kif("text"), "value"),
        Output(kif("text-load"), "disabled"),
        prevent_initial_call=True,
    )
    def enable_load_button(value):
        if not value:
            return True
        return False

def make_input_file():

    return [
        dcc.Upload(
            id=kif("file"),
            children=["Drop or ", html.A("Select a file")],
            style = KMVIZ_UPLOAD_STYLE
        ),
        html.Div(id=kif("file-error"))
    ]

def make_input_file_callbacks():

    @callback(
        Input(kif("file"), "filename"),
        Input(kif("file"), "contents"),
        Output(ksfr("query-sequences"), "data"),
        Output(kif("file-error"), "children"),
        Output(kif("file"), "style"),
        Output(kif("file"), "filename"),
        Output(kif("select"), "style"),
        prevent_initial_call=True,
    )
    def load_input_from_file(filename, contents):
        prevent_update_on_none(filename, contents)

        content_type, data = contents.split(",")
        content = base64.b64decode(data).decode("utf-8")

        try:
            queries = [Query(name, seq) for name, seq, _ in parse_fastx(content, state.kmstate.limits)]
            query = "queries" if len(queries) > 1 else "query"
            message = dmc.Text(f"🗎 {filename} ({len(queries)} {query})", weight=500)
            return (
                Serverside(queries),
                message,
                style_hide_patch(),
                None,
                style_hide_patch()
            )
        except KmVizIOError as e:
            message = dmc.Text(f"🗎 {filename}: '{str(e)}'", color="red", weight=500)
            return Serverside([]), message, no_update, None, no_update

def make_input_session_file():
    return [
        dcc.Upload(
            dmc.Button(
                "Upload session",
                size="xs",
                color = "#1C7ED6",
                style = {"margin-top": "2px"},
                leftIcon=DashIconify(icon="bi:filetype-json", width=20)
            ),
            id=kif("session-file"),
        ),
        html.Div(id=kif("session-file-error"))
    ]

def make_input_session_file_callbacks():
    @callback(
        Input(kif("session-file"), "filename"),
        Input(kif("session-file"), "contents"),
        Output(ksf("query-results"), "data"),
        Output(kf.sid("plot-only"), "data"),
        Output(kgsf("provider"), "data"),
        Output(kgsf("provider"), "value"),
        Output(kgsf("query"), "data"),
        Output(kgsf("query"), "value"),
        Output("tab-select", "value"),
        Output(kif("session-file"), "filename"),
        Output(kf.sid("sidebar-layout"), "style"),
        Output(kif("session-file-error"), "children"),
        prevent_initial_call=True,
    )
    def input_session_file(filename, contents):
        try:
            content_type, data = contents.split(",")
            content = base64.b64decode(data).decode()
            session = orjson.loads(content)

            result = {}
            providers = []
            queries = []
            geo = {}
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

            return Serverside(result), {"session": geo}, pdata, providers[0], qdata, queries[0], "table", None, {"display":"none"}, []
        except Exception as e:
            message = dmc.Text("An error occured while loading your session file", color="red", weight=500)
            ret = html.Div([message], style={"margin-left":"10px", "margin-top": "3px"})
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, None, no_update, ret

def make_input():
    hidden = { "display": "none" }
    show = { "display": "inline" }

    res = html.Div([
        dmc.Divider(size="sm", color="gray", label="INPUT", labelPosition="center"),
        dmc.Space(h=5),

        dmc.SegmentedControl(
            id=kif("select"),
            orientation="horizontal",
            size="sm",
            fullWidth=True,
            style={},
            color="#1C7ED6",
            data=make_select_data(["text", "file", "session"], True)
        ),


        dmc.Space(h=10),

        html.Div(make_input_text(), id=kidf("text"), style=show),
        html.Div(make_input_file(), id=kidf("file"), style=hidden),
        html.Div(make_input_session(), id=kidf("session"), style=hidden),
    ])

    return res

def make_input_callbacks():

    @callback(
        Input(kif("select"), "value"),
        State(kidf.all, "id"),
        Output(kidf.all, "style"),
        prevent_initial_call=True,
    )
    def show_input(input_type, idx):
        prevent_update_on_none(input_type)
        styles = [{"display": "none"} for _ in range(len(idx))]

        if not input_type:
            return styles

        for index, id in enumerate(idx):
            if id["index"] == input_type:
                styles[index]["display"] = "inline"

        return styles

    make_input_text_callbacks()
    make_input_file_callbacks()
    make_input_session_callbacks()


