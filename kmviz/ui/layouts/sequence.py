from dash_extensions.enrich import html, dash_table, Input, Output, dcc, State, callback
import dash_mantine_components as dmc
from dash import no_update
import plotly.express as px
import plotly.graph_objects as go

from kmviz.ui.utils import make_select_data, prevent_update_on_none
from kmviz.ui.components.figure import make_plot_title, make_plot_title_callbacks
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
    res =  html.Div([
        dmc.Group([
            dmc.Select(
                id=kseq.sid("select"),
                label="Select ID"
            )
        ]),

        dcc.Graph(
            figure=blank_figure(),
            id=kseq.sid("figure"),
            responsive=True,
            style = { "margin-left": "auto", "margin-right": "auto", "height": "50vh", "width": "95%" }
        ),

        make_plot_title(kseq.child("title")),
    ])

    return res

def make_sequence_layout_callbacks():

    @callback(
        Input(kgsf("provider"), "value"),
        Input(kgsf("query"), "value"),
        State(ksf("query-results"), "data"),
        Output(kseq.sid("select"), "data"),
        Output(kseq.sid("select"), "value"),
        Output(kseq.sid("panel"), "disabled"),
        prevent_initial_callbacks=True,
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
        prevent_initial_callbacks=True
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
        prevent_initial_callbacks=True,
    )
    def update_sequence_graph(sample, provider, query, query_result):
        if provider.startswith("__kmviz_df"):
            prevent_update_on_none(None)

        prevent_update_on_none(sample, provider, query)

        qr = query_result[query][provider]

        f = {'ID': {'filterType': 'text', 'type': 'contains', 'filter': sample}}

        index = list(range(len(qr.query.seq)))

        if qr.response[sample].has_abs():
            fig = px.line(x=index, y=qr.response[sample].covyb, line_shape="linear")
        else:
            fig = px.line(x=index, y=qr.response[sample].covxb, line_shape="hv")

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

        return fig

    make_plot_title_callbacks(kseq.child("title"), kseq.sid("figure"))

