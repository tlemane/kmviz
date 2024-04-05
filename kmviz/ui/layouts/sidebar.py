import dash_mantine_components as dmc
from dash_extensions.enrich import html, callback, dcc, Input, Output, State, Serverside

from kmviz import __version__ as kmviz_version

from kmviz.ui.id_factory import kmviz_factory as kf
from kmviz.ui.components.select import make_select_provider, make_select_provider_callbacks
from kmviz.ui.components.input import make_input, make_input_callbacks, KMVIZ_UPLOAD_STYLE
from kmviz.ui.components.option import make_config, make_config_callbacks
from kmviz.ui.components.submit import make_submit, make_submit_callbacks
from kmviz.core.io import KmVizIOError

from kmviz.ui.utils import prevent_update_on_none
import base64
import pandas as pd
from io import StringIO, BytesIO


from kmviz.ui import state
klf = kf.child("layout")
ksb = klf.child("ksb")

def make_sidebar_layout():

    if state.kmstate.plot_only:
        res = html.Div([
            dcc.Store(id=kf.sid("plot-only"), data={}),
            dmc.Center([
                html.H1(f"kmviz v{kmviz_version}"),
            ]),
            html.H4(f"Plot only mode"),
            dmc.Divider(size="sm", color="gray", label="INPUT (csv/tsv/xlsx)", labelPosition="center"),
            dcc.Upload(
                id=ksb.sid("dataframe"),
                children=["Drop or ", html.A("Select a file")],
                style = KMVIZ_UPLOAD_STYLE
            ),
            dmc.Divider(size="sm", color="gray", label="CONFIG", labelPosition="center"),
            dmc.Group([
                dmc.TextInput(
                    label="Index column",
                    id=ksb.sid("index-column"),
                    style = {"width": "100px"}
                ),
                dmc.TextInput(
                    label="Separator",
                    id=ksb.sid("separator"),
                    style = {"width": "100px"}
                )
            ]),
            dmc.Group([
                dmc.TextInput(
                    label="Latitude column",
                    id=ksb.sid("latitude"),
                    style = {"width": "100px"}
                ),
                dmc.TextInput(
                    label="Longitude column",
                    id=ksb.sid("longitude"),
                    style = {"width": "100px"}
                )
            ]),
            dmc.Space(h=5),
            html.Div(id=ksb.sid("dataframe-error")),
            dmc.Space(h=5),
            dmc.Button(
                "Load",
                id=ksb.sid("df-button"),
            ),

        ], className="sidebar", id=ksb.sid("div"))
    else:
        res = html.Div([
            dcc.Store(id=kf.sid("plot-only"), data={}),
            dmc.Center([
                html.H1(f"kmviz v{kmviz_version}"),
            ]),
            dmc.Space(h=5),
            make_select_provider(),
            dmc.Space(h=20),
            make_input(),
            dmc.Space(h=20),
            make_config(),
            dmc.Space(h=20),
            make_submit()
        ], className="sidebar", id=ksb.sid("div"))

    return res

def make_sidebar_layout_callbacks():

    if state.kmstate.plot_only:
        @callback(
            Input(ksb.sid("dataframe"), "filename"),
            Output(ksb.sid("dataframe-error"), "children"),
        )
        def show_filename(filename):
            return dmc.Text(f"🗎 {filename}", weight=500)

        @callback(
            Input(ksb.sid("df-button"), "n_clicks"),
            State(ksb.sid("dataframe"), "filename"),
            State(ksb.sid("dataframe"), "contents"),
            State(ksb.sid("separator"), "value"),
            State(ksb.sid("index-column"), "value"),
            State(ksb.sid("latitude"), "value"),
            State(ksb.sid("longitude"), "value"),
            Output(kf.sid("plot-only"), "data"),
            Output(ksb.sid("dataframe-error"), "children"),

            prevent_initial_callbacks=True,
            prevent_initial_call=True,
        )
        def load_df_file(button, filename, contents, sep, index, lat, lon):

            hide = {"display": "none"}
            prevent_update_on_none(filename, contents)
            content_type, data = contents.split(",")
            content = base64.b64decode(data)

            try:
                df = None
                if filename.endswith("csv") or filename.endswith("tsv"):
                    pdio = StringIO(content.decode("utf-8"))
                    try:
                        if sep:
                            df = pd.read_csv(pdio, sep=sep)
                        else:
                            df = pd.read_csv(pdio)
                    except:
                        raise KmVizIOError(f"Error while loading '{filename}'")
                else:
                    pdio = BytesIO(content)
                    try:
                        df = pd.read_excel(pdio)
                    except:
                        raise KmVizIOError(f"Error while loading '{filename}'")

                res = {}

                if not index or index not in list(df):
                    raise KmVizIOError(f"'{index}' not found in dataframe.")

                df.rename(columns={index : "ID"}, inplace=True)
                res["df"] = df

                res["geodata"] = None
                if lat and lon:
                    if lat in list(df) and lon in list(df):
                        res["geodata"] = { "latitude": lat, "longitude": lon}
                    else:
                        raise KmVizIOError(f"'{lat}' or '{lon}' not found in dataframe")

                return Serverside(res), dmc.Text(f"🗎 {filename}", weight=500)
            except KmVizIOError as e:
                return Serverside(res), dmc.Text(str(e), color="red", weight=500)

    else:
        make_select_provider_callbacks()
        make_input_callbacks()
        make_config_callbacks()
        make_submit_callbacks()
