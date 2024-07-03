from dash_extensions.enrich import html, dash_table, Input, Output, dcc, State, callback
import dash_mantine_components as dmc
from dash import no_update
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import plotly.io as pio

from dash_iconify import DashIconify

from kmviz.ui.utils import make_select_data, prevent_update_on_none
from kmviz.ui.components.figure import make_plot_title, make_plot_title_callbacks, make_select_input
from kmviz.ui.components.select import kgsf
from kmviz.ui.components.store import ksf
from kmviz.ui.layouts.table import ktable

from kmviz.ui.id_factory import kmviz_factory as kf

kseq = kf.child("seq")

def blank_figure():
    fig = go.Figure(go.Scatter(x=[], y = []))
    fig.update_layout(template = "seaborn")
    fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
    fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)

    return fig

def make_sequence_layout():

    down_select = make_select_input(
        kseq.sid("down-select"),
        label=None,
        data=make_select_data(["png", "jpg", "svg", "pdf", "webp", "html", "json"]),
        placeholder="format",
        clearable=False,
        icon=DashIconify(icon="material-symbols:download", width=20),
        value="png",
        searchable=True,
    )

    res =  html.Div([
        dmc.Group([
            dmc.Select(
                id=kseq.sid("select"),
                label="Select ID"
            ),
            dmc.ActionIcon(
                DashIconify(icon="bi:filetype-json", width=20),
                id=kseq.sid("down-data-button"),
                variant="filled",
                color = "#1C7ED6"
            ),
            dcc.Download(id=kseq.sid("download-data")),
            dmc.Group([
                down_select,
                dmc.ActionIcon(
                    DashIconify(icon="material-symbols:download", width=20),
                    id=kseq.sid("down-button"),
                    variant="filled",
                    color = "#1C7ED6",
                ),
            ], style = {"margin-left":"auto", "margin-right": 0, "width": "fit-content"}, spacing=5),
        ]),

        dcc.Graph(
            figure=blank_figure(),
            id=kseq.sid("figure"),
            responsive=True,
            style = { "margin-left": "auto", "margin-right": "auto", "height": "50vh", "width": "95%" }
        ),

        make_plot_title(kseq.child("title")),

        dcc.Download(id=kseq.sid("download")),
    ])

    return res

def make_sequence_layout_callbacks():

    @callback(
        Input(kseq.sid("down-button"), "n_clicks"),
        State(kseq.sid("down-select"), "value"),
        State(kseq.sid("figure"), "figure"),
        Output(kseq.sid("download"), "data"),
        prevent_initial_call=True,
    )
    def download_cov(n_clicks, fmt, data):
        if n_clicks:
            if fmt == "html":
                content = pio.to_html(data, validate=False)
                return dict(content=content, filename="kmviz-cov.html")
            elif fmt == "json":
                content = pio.to_json(data, validate=False)
                return dict(content=content, filename="kmviz-cov.json")
            else:
                content = pio.to_image(data, fmt, validate=False)
                return dcc.send_bytes(content, f"kmviz-cov.{fmt}")

    @callback(
        Input(kseq.sid("down-data-button"), "n_clicks"),
        State(kgsf("provider"), "value"),
        State(kgsf("query"), "value"),
        State(ksf("query-results"), "data"),
        Output(kseq.sid("download-data"), "data"),
        prevent_initial_call=True,
    )
    def download_json(n_clicks, provider, query, query_result):
        if n_clicks:
            if provider.startswith("__kmviz_df"):
                prevent_update_on_none(None)

            prevent_update_on_none(provider, query)

            qr = query_result[query][provider]

            res = {}
            res[query] = {}

            for sample, resp in qr.response.items():
                if resp.has_abs():
                    res[query][sample] = {"ykmer": resp.covyk, "ybase": resp.covyb}
                else:
                    res[query][sample] = {"xkmer": resp.covxk, "xbase": resp.covxb}

            return dict(content=str(res), filename=f"{provider}-{query}.json")

    @callback(
        Input(kgsf("provider"), "value"),
        Input(kgsf("query"), "value"),
        State(ksf("query-results"), "data"),
        Output(kseq.sid("select"), "data"),
        Output(kseq.sid("select"), "value"),
        Output(kseq.sid("panel"), "disabled"),
        prevent_initial_call=True,
    )
    def update_sample_select(provider, query, query_result):
        prevent_update_on_none(provider, query)

        if provider.startswith("__kmviz_df"):
            prevent_update_on_none(None)

        qr = query_result[query][provider]
        ids = list(qr.df["ID"])
        if not ids:
            return no_update, no_update, True
        return make_select_data(ids), ids[0], False

    @callback(
        Input(ktable.sid("grid"), "selectedRows"),
        Output(kseq.sid("select"), "value"),
        Output("tab-select", "value"),
        prevent_initial_call=True
    )
    def on_selected(data):
        if not len(data):
            prevent_update_on_none(None)

        return data[0]["ID"], "sequence"

    @callback(
        Input(kseq.sid("select"), "value"),
        Input(kgsf("provider"), "value"),
        Input(kgsf("query"), "value"),
        State(ksf("query-results"), "data"),
        Output(kseq.sid("figure"), "figure"),
        prevent_initial_call=True,
    )
    def update_sequence_graph(sample, provider, query, query_result):
        if provider.startswith("__kmviz_df"):
            prevent_update_on_none(None)

        prevent_update_on_none(sample, provider, query)

        qr = query_result[query][provider]

        f = {'ID': {'filterType': 'text', 'type': 'contains', 'filter': sample}}

        index = list(range(len(qr.query.seq)))

        m = []
        cols = ["base"]

        if qr.response[sample].k:
            m = [None] * (qr.response[sample].k-1)
            cols = ["kmer", "base"]

        if qr.response[sample].has_abs():
            df = pd.DataFrame({"Sequence": index, "kmer": qr.response[sample].covyk + m, "base": qr.response[sample].covyb})
            fig = px.line(df, x="Sequence", y=cols, line_shape="linear", markers=True)
        else:
            df = pd.DataFrame({"Sequence": index, "kmer": qr.response[sample].covxk + m, "base": qr.response[sample].covxb})
            fig = px.line(df, x="Sequence", y=cols, line_shape="linear", markers=True)

        fig.update_layout(
            xaxis = dict(
                tickmode = 'array',
                tickvals = index,
                ticktext = [x for x in qr.query.seq]
            )
        )

        fig.update_layout(
            xaxis=dict(rangeslider=dict(visible=True,range=[0, len(qr.query.seq)]),
                       range=[0, 50],
                       type="category")
        )

        fig.update_layout(legend_title_text="")
        fig.update_xaxes(title_text="Sequence")

        return fig

    make_plot_title_callbacks(kseq.child("title"), kseq.sid("figure"))

