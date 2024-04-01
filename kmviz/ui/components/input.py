import base64

from dash import Patch, no_update
import dash_mantine_components as dmc
from dash_extensions.enrich import Input, Output, State, html, dcc, Serverside, callback

from kmviz.ui.id_factory import kmviz_factory as kf
from kmviz.ui.patch import style_hide_patch, style_inline_patch
from kmviz.ui.components.store import ksfr
from kmviz.ui.utils import prevent_update_on_none

from kmviz.core.query import Query
from kmviz.core.io import parse_fastx, KmVizIOError
from kmviz.ui import state
from kmviz.ui.components.store import ksf
from kmviz.ui.components.select import kgsf
kif = kf.child("input")
kidf = kif.child("div")

def make_input_session():
    return [
        dmc.TextInput(
            id=kif("session"),
            required=True,
            label="Session ID",
            placeholder="kmviz-324bfabc-50e7-44ac-89d9-6460803d2f5e"
        ),
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
        prevent_initial_callbacks=True,
        prevent_initial_call=True,
    )
    def load_session(n_clicks, session_id):
        if n_clicks:
            try:
                res = state.kmstate.get_result(session_id)
                return Serverside(res[0]), res[1], res[2], res[3], res[4], {"display":"none"}, no_update
            except:
                msg = "Session not found. Invalid session id, query still running, or results erased."
                return no_update, no_update, no_update, no_update, no_update, no_update, msg


def make_input_text():
    return [
        dmc.Textarea(
            id=kif("text"),
            label="Query sequence(s)",
            description="Fasta/Fastq format",
            placeholder="Sequences...",
            spellCheck=False,
            autosize=True,
            maxRows=4,
            required=True,
            style={"display":"inline"}
        ),
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
        prevent_initial_callbacks=True,
        prevent_initial_call=True,
    )
    def load_input_from_text(n_clicks, content):
        if n_clicks:
            try:
                queries = [Query(name, seq) for name, seq, _ in parse_fastx(content)]
                query = "queries" if len(queries) > 1 else "query"
                message = dmc.Text(f"🗎 raw ({len(queries)} {query})", weight=500)
                return Serverside(queries), style_hide_patch(), None, message, style_hide_patch(), style_hide_patch()
            except KmVizIOError as e:
                return Serverside([]), Patch(), str(e), None, no_update, style_inline_patch()

    @callback(
        Input(kif("text"), "value"),
        Output(kif("text-load"), "disabled"),
        prevent_initial_callbacks=True,
        prevent_initial_call=True,
    )
    def enable_load_button(value):
        if not value:
            return True
        return False

def make_input_file():

    upload_style = {
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

    return [
        dcc.Upload(
            id=kif("file"),
            children=["Drop or ", html.A("Select a file")],
            style = upload_style
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
        prevent_initial_callbacks=True,
        prevent_initial_call=True,
    )
    def load_input_from_file(filename, contents):
        prevent_update_on_none(filename, contents)

        content_type, data = contents.split(",")
        content = base64.b64decode(data).decode()

        try:
            queries = [Query(name, seq) for name, seq, _ in parse_fastx(content)]
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
            message = dmc.Text(f"🗎 {filename} -> Invalid format", color="red", weight=500)
            return Serverside([]), message, Patch(), None, style_inline_patch()



def make_input():
    hidden = { "display": "none" }

    res = html.Div([
        dmc.Divider(size="sm", color="gray", label="INPUT", labelPosition="center"),

        dmc.RadioGroup(
            [dmc.Radio("Text", "text"), dmc.Radio("File", "file"), dmc.Radio("Session", "session")],
            id=kif("select"),
            label="Select input type",
            withAsterisk=True,
            style={"display":"inline"}
        ),

        dmc.Space(h=10),

        html.Div(make_input_text(), id=kidf("text"), style=hidden),
        html.Div(make_input_file(), id=kidf("file"), style=hidden),
        html.Div(make_input_session(), id=kidf("session"), style=hidden),
    ])

    return res

def make_input_callbacks():

    @callback(
        Input(kif("select"), "value"),
        State(kidf.all, "id"),
        Output(kidf.all, "style"),
        prevent_initial_callbacks=True,
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

